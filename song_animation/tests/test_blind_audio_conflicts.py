import json,tempfile,unittest
from unittest.mock import patch
from song_animation.audio_lyrics import confirm_conflicts_from_audio
from song_animation.provider import ProviderUnavailable

class BlindAudioConflict(unittest.TestCase):
    def call(self,reply):
        segments=[{'start':0,'end':3,'text':'a sunflower blooms'}]
        conflicts=[{'start':.5,'end':1.5,'decoder_words':'sun flower','proposed':'a sunflower blooms'}]
        with tempfile.TemporaryDirectory() as td,patch('song_animation.audio_lyrics.generate_json',return_value=reply) as model:
            result=confirm_conflicts_from_audio({'inline_data':{'mime_type':'audio/mpeg','data':'actual-audio'}},td,segments,conflicts)
            return result,model.call_args

    def test_word_boundary_difference_needs_matching_blind_audio_and_full_model(self):
        result,args=self.call({'regions':[{'region':0,'text':'A sun flower blooms.','uncertain':False}],'_provider_model':'gemini-full'})
        self.assertEqual(result['_provider_model'],'gemini-full')
        self.assertTrue(args.kwargs['require_full_model'])
        # Neither candidate phrase is leaked into the independent listening call.
        self.assertNotIn('sunflower',args.args[0]);self.assertNotIn('sun flower',args.args[0])
        self.assertIn('TIME WINDOWS',args.args[0]);self.assertIn('audio_part',args.kwargs)

    def test_positive_verdict_different_verb_lite_uncertainty_and_missing_regions_hold(self):
        bad=[{'valid':True,'_provider_model':'gemini-full'},
             {'regions':[{'region':0,'text':'a sunflower withers','uncertain':False}],'_provider_model':'gemini-full'},
             {'regions':[{'region':0,'text':'a sunflower blooms','uncertain':False}],'_provider_model':'gemini-flash-lite'},
             {'regions':[{'region':0,'text':'a sunflower blooms','uncertain':True}],'_provider_model':'gemini-full'},
             {'regions':[],'_provider_model':'gemini-full'}]
        for reply in bad:
            with self.subTest(reply=reply),self.assertRaises(ValueError):self.call(reply)

    def test_service_outage_is_not_relabelled_wrong_lyrics(self):
        with tempfile.TemporaryDirectory() as td,patch('song_animation.audio_lyrics.generate_json',side_effect=ProviderUnavailable([{'model':'full','http_status':429}])):
            with self.assertRaises(ProviderUnavailable):confirm_conflicts_from_audio({},td,[{'start':0,'end':3,'text':'actual phrase'}],[{'start':0,'end':1}])

    def test_devanagari_half_r_variant_does_not_equate_different_words(self):
        for heard,accepted in [('कल सरदी होगी',True),('कल गरमी होगी',False),('न कल सर्दी होगी',False)]:
            reply={'regions':[{'region':0,'text':heard,'uncertain':False}],'_provider_model':'gemini-full'}
            with self.subTest(heard=heard),tempfile.TemporaryDirectory() as td,patch('song_animation.audio_lyrics.generate_json',return_value=reply):
                args=({},td,[{'start':0,'end':3,'text':'कल सर्दी होगी'}],[{'start':1,'end':2}])
                if accepted:self.assertEqual(confirm_conflicts_from_audio(*args),reply)
                else:
                    with self.assertRaises(ValueError):confirm_conflicts_from_audio(*args)

    def test_blind_production_request_receives_physical_audio_crops_not_the_full_song(self):
        from pathlib import Path
        import base64
        def crop(cmd,**kwargs):Path(cmd[-1]).write_bytes(b'only the requested audio interval')
        reply={'regions':[{'region':0,'text':'a sunflower blooms','uncertain':False}],'_provider_model':'gemini-full'}
        with tempfile.TemporaryDirectory() as td,patch('song_animation.audio_lyrics.subprocess.run',side_effect=crop) as ffmpeg,patch('song_animation.audio_lyrics.generate_json',return_value=reply) as model:
            confirm_conflicts_from_audio({'inline_data':{'data':'full-song-should-not-be-sent'}},td,[{'start':2,'end':5,'text':'a sunflower blooms'}],[{'start':3,'end':4}],audio='actual-source.wav',language='English')
            cmd=ffmpeg.call_args.args[0];self.assertEqual(cmd[cmd.index('-ss')+1],'2');self.assertEqual(cmd[cmd.index('-t')+1],'3')
            self.assertNotIn('audio_part',model.call_args.kwargs)
            raw=model.call_args.kwargs['extra_parts'][1]['inline_data']['data']
            self.assertEqual(base64.b64decode(raw),b'only the requested audio interval')

    def test_provider_resume_keeps_candidate_and_asr_but_still_requires_audio_review(self):
        from pathlib import Path
        from song_animation.audio_lyrics import analyze_audio
        data={'language':'English','has_vocals':True,'segments':[{'text':'walk beside me','start':0,'end':2,'uncertain':False}],'unclear':[],'instrumental':[]}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);audio=root/'source.wav';audio.write_bytes(b'actual selected source')
            def convert(cmd,**kwargs):Path(cmd[-1]).write_bytes(b'analysis mp3')
            with patch('song_animation.audio_lyrics.duration',return_value=3),patch('song_animation.audio_lyrics.subprocess.run',side_effect=convert),patch('song_animation.lyrics.preflight'),patch('song_animation.recognition.independent_audio_text',return_value={'status':'available','words':[]}) as asr:
                with patch('song_animation.audio_lyrics.generate_json',side_effect=[data,ProviderUnavailable([{'model':'full','http_status':429}])]):
                    with self.assertRaises(ProviderUnavailable):analyze_audio(audio,root)
                self.assertTrue((root/'audio_candidate.json').exists());self.assertFalse((root/'lyrics.json').exists())
                with patch('song_animation.audio_lyrics.generate_json',return_value={'valid':True}) as model:
                    result=analyze_audio(audio,root)
                    model.assert_called_once();self.assertTrue(model.call_args.kwargs['require_full_model'])
                asr.assert_called_once();self.assertEqual(result['words'][0]['text'],'walk beside me');self.assertFalse((root/'audio_candidate.json').exists())

    def test_changed_audio_cannot_reuse_pending_transcript(self):
        from pathlib import Path
        from song_animation.audio_lyrics import analyze_audio
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);audio=root/'source.wav';audio.write_bytes(b'new source')
            (root/'audio_candidate.json').write_text(json.dumps({'key':'some-other-audio','data':{'segments':[{'text':'old source words'}]}}))
            def convert(cmd,**kwargs):Path(cmd[-1]).write_bytes(b'analysis mp3')
            with patch('song_animation.audio_lyrics.duration',return_value=3),patch('song_animation.audio_lyrics.subprocess.run',side_effect=convert),patch('song_animation.audio_lyrics.generate_json',side_effect=ProviderUnavailable([{'model':'full','http_status':429}])) as model:
                with self.assertRaises(ProviderUnavailable):analyze_audio(audio,root)
                self.assertEqual(model.call_args.kwargs['tag'],'audio_lyrics')
