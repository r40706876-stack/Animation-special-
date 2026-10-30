import copy,json,subprocess,tempfile,unittest
from pathlib import Path
from PIL import ImageChops
from song_animation.vector import validate_vector,sanitize_svg,render_vector
from song_animation.contract import validate

class VectorContract(unittest.TestCase):
    def setUp(self):self.p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
    def test_new_non_rose_subjects_render_and_move(self):
        validate(self.p)
        for i,s in enumerate(self.p['scenes']):
            a=render_vector(self.p,i,s['start_frame']+5);b=render_vector(self.p,i,s['end_frame']-10)
            self.assertIsNotNone(ImageChops.difference(a,b).getbbox())
    def test_network_script_and_embedded_images_rejected(self):
        for body in ['<script>alert(1)</script>','<image href="file:///etc/passwd"/>','<rect width="5" height="5" fill="url(https://x)"/>','<path d="M0 0L2 2" onclick="x()"/>']:
            with self.assertRaises(ValueError):sanitize_svg('<svg xmlns="http://www.w3.org/2000/svg">'+body+'</svg>')
    def test_identical_whole_picture_pan_is_not_two_independent_actions(self):
        s=self.p['scenes'][0]
        for n in s['nodes'][1:]:
            n['wave']={};n['keys'][1]=dict(n['keys'][0],t=1,x=n['keys'][0]['x']+20)
        with self.assertRaisesRegex(ValueError,'independent'):validate(self.p)
    def test_parent_cycle_rejected(self):
        self.p['scenes'][0]['nodes'][1]['parent']='kite'
        with self.assertRaises(ValueError):validate(self.p)
    def test_generated_duration_cannot_exceed_thirty_seconds(self):
        self.p['total_frames']=721
        with self.assertRaises(ValueError):validate(self.p)

class ClipTests(unittest.TestCase):
    def test_long_source_trims_and_short_source_is_not_stretched(self):
        from song_animation.clip import prepare
        for seconds in (2.5,31):
            with tempfile.TemporaryDirectory() as td:
                root=Path(td);audio=root/'source.wav'
                subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i',f'sine=frequency=330:duration={seconds}','-ar','22050',str(audio)],check=True)
                _,selection=prepare(audio,root/'out')
                self.assertAlmostEqual(selection['duration'],min(30,seconds),places=2)
                self.assertFalse(selection['short_inputs_padded'])

class StoryboardTests(unittest.TestCase):
    def test_tiny_instrumental_ending_merges_without_losing_lyrics(self):
        from song_animation.generative import compile_storyboard
        lyrics={'duration':6,'timing_granularity':'phrase','words':[{'text':'a phrase','start':0,'end':5.5}]}
        raw={'bible':{'style':'daylight'},'scenes':[{'start':0,'label':'a meaningful journey','visual':'a person on a hill','action':'walk and wave a hand','lyric_ids':[0]},{'start':5.8,'label':'a short ending','visual':'the same hill','action':'the person settles','lyric_ids':[]}]}
        p=compile_storyboard(raw,lyrics)
        self.assertEqual(len(p['scenes']),1)
        self.assertEqual(p['scenes'][0]['lyric_ids'],[0])
        self.assertEqual(p['scenes'][0]['end_frame'],144)
        self.assertTrue(p['timeline_adjustments'])

class GeneratedRecovery(unittest.TestCase):
    def test_complete_first_object_survives_trailing_duplicate_json(self):
        from song_animation.provider import parse_object
        self.assertEqual(parse_object('{"assets":[],"nodes":[]}\n{"notes":"extra"}'),{'assets':[],'nodes':[]})
    def test_bad_package_json_has_one_bounded_repair(self):
        from unittest.mock import patch
        from song_animation.generative import scene_package
        p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
        p['bible']={'style':'bright daylight'}
        for s in p['scenes']:s.update(visual=s['label'],action='independent character and prop movement')
        data={'background':p['scenes'][0]['background'],'assets':[dict(v,id=k) for k,v in p['assets'].items()],'nodes':p['scenes'][0]['nodes']}
        with tempfile.TemporaryDirectory() as td,patch('song_animation.generative.generate_json',side_effect=[json.JSONDecodeError('truncated','{',1),data]) as api:
            scene,assets=scene_package(p,0,td,{})
            self.assertEqual(api.call_count,2)
            self.assertEqual(scene['kind'],'vector')
