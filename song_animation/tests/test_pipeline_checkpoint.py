import copy,hashlib,json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from song_animation.pipeline_checkpoint import identity,load,save
from song_animation.provider import generate_json,ProviderUnavailable

class DurablePipeline(unittest.TestCase):
    def plan(self):return json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())

    def test_repaired_plan_survives_restart_only_for_exact_audio_and_settings(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);audio=p/'song.wav';audio.write_bytes(b'original selected audio')
            lyrics={'words':[]};key=identity(audio,lyrics,'generated','flux-layers',1080)
            plan=self.plan();save(p,key,plan,1)
            self.assertEqual(load(p,key)['pass_index'],1)
            self.assertIsNone(load(p,identity(audio,lyrics,'generated','flux-layers',540)))
            audio.write_bytes(b'another song');self.assertIsNone(load(p,identity(audio,lyrics,'generated','flux-layers',1080)))

    def test_pending_repair_requires_its_actual_review_frames(self):
        with tempfile.TemporaryDirectory() as td:
            save(td,'source-key',self.plan(),1,{'issues':[{'shot':0,'issue':'visible defect'}]},[0],True)
            self.assertIsNone(load(td,'source-key'))
            Path(td,'review_contact.jpg').write_bytes(b'frame cache')
            self.assertEqual(load(td,'source-key')['completed_shots'],[0])

    def test_invalid_or_corrupt_cache_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td,'pipeline_checkpoint.json').write_text('{bad');self.assertIsNone(load(td,'source-key'))
            save(td,'source-key',self.plan(),True)
            self.assertIsNone(load(td,'source-key'))

    def test_successful_fallback_does_not_recall_exhausted_model_for_every_asset(self):
        listing=Mock();listing.json.return_value={'models':[{'name':'models/'+m,'supportedGenerationMethods':['generateContent']} for m in ['gemini-3-flash-preview','gemini-3.5-flash']]}
        good=Mock(status_code=200);good.json.return_value={'candidates':[{'content':{'parts':[{'text':'{"valid":true}'}]}}]}
        calls=[]
        def post(url,**kwargs):calls.append(url);return Mock(status_code=429) if '/gemini-3-flash-preview:' in url else good
        with patch.dict(os.environ,{'GEMINI_API_KEY':'test-key','GEMINI_MODEL':'','SONG_PROVIDER_SKIP_MODELS':'[]'}),patch('requests.get',return_value=listing),patch('requests.post',side_effect=post):
            generate_json('asset one',prefer_quality=True);generate_json('asset two',prefer_quality=True)
            self.assertEqual(sum('/gemini-3-flash-preview:' in u for u in calls),1)
            self.assertEqual(sum('/gemini-3.5-flash:' in u for u in calls),2)

    def test_provider_outage_during_repair_is_not_treated_as_a_bad_drawing(self):
        from PIL import Image
        from song_animation.review import refine
        with tempfile.TemporaryDirectory() as td:
            Image.new('RGB',(540,320),'white').save(Path(td,'review_contact.jpg'))
            with patch('song_animation.generative.scene_package',side_effect=ProviderUnavailable([{'model':'busy','http_status':503}])):
                with self.assertRaises(ProviderUnavailable):refine(self.plan(),td,{'issues':[{'shot':0,'issue':'repair artwork'}]})

    def test_initial_branch_upload_does_not_reprocess_inherited_songs(self):
        from song_animation.select_inputs import select
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);folder=root/'song_animation/inputs';folder.mkdir(parents=True)
            (folder/'old.wav').write_bytes(b'old');(folder/'new.wav').write_bytes(b'new')
            diff=subprocess.CompletedProcess([],0,stdout=b'song_animation/inputs/new.wav\0',stderr=b'')
            with patch('song_animation.select_inputs.subprocess.run',return_value=diff) as git:
                self.assertEqual(select(root,'0'*40,'new-head'),['song_animation/inputs/new.wav'])
                self.assertIn('--root',git.call_args.args[0])
