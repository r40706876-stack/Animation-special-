import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from song_animation.quality import QualityHold
from song_animation.tests.test_quality_gate import clear_review

class CompositionPreflight(unittest.TestCase):
    def test_composition_samples_need_no_encoded_video_and_are_labelled(self):
        from song_animation.review import review
        plan=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
        with tempfile.TemporaryDirectory() as td,patch('song_animation.art.render_frame',return_value=Image.new('RGB',(540,960),'beige')) as draw,patch('song_animation.review.encoded_sample') as decode,patch('song_animation.review.generate_json',return_value=clear_review()) as model,patch('song_animation.film_standard.reference_parts',return_value=[]):
            result=review(plan,td,source='composition')
            self.assertEqual(draw.call_count,3*len(plan['scenes']));decode.assert_not_called()
            self.assertEqual(result['sample_source'],'composition')
            self.assertIn('before video encoding',model.call_args.args[0])
            self.assertTrue(Path(td,'composition_review.json').exists())

    def test_bad_raster_composition_saves_repair_and_skips_full_export(self):
        from song_animation.run import main
        plan=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
        bad=clear_review();bad['reference_quality_met']=False
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);audio=root/'audio.wav';audio.write_bytes(b'source')
            lyrics=root/'lyrics.json';lyrics.write_text(json.dumps({'duration':12,'words':[]}));out=root/'out'
            with patch('sys.argv',['song','--audio',str(audio),'--out',str(out),'--lyrics',str(lyrics),'--artwork','flux-layers']),patch('song_animation.run.prepare',return_value=(audio,{'duration':12})),patch('song_animation.run.music_features',return_value={}),patch('song_animation.generative.build',return_value=plan),patch('song_animation.original_art.paint',return_value=plan),patch('song_animation.review.review',return_value=bad),patch('song_animation.run.render') as export:
                with self.assertRaises(QualityHold):main()
                export.assert_not_called()
            state=json.loads((out/'status.json').read_text())
            self.assertEqual(state['stage'],'composition_preflight')
            self.assertTrue(state['automatic_repair_pending'])
            self.assertTrue(json.loads((out/'pipeline_checkpoint.json').read_text())['pending_repair'])
