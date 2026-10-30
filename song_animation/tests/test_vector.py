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
        raw['story']={'premise':'A traveller reaches a friend','emotional_goal':'Share a small happy reunion','opening':'Waiting on the hill alone','turning_point':'A familiar friend waves back','payoff':'The traveller settles beside the friend','entities':{'traveller':{'description':'Traveller in one stable outfit','initial_state':'Alone at the hill entrance'}}}
        raw['scenes'][0]['story']={'purpose':'Reach the meeting point','link_from_previous':'Opening setup on the hill','emotional_change':'Anticipation becomes recognition','state_in':{'traveller':'Alone at the hill entrance'},'state_out':{'traveller':'Arrived and waving to friend'}}
        raw['scenes'][1]['story']={'purpose':'Resolve the meeting gently','link_from_previous':'The friend has waved back','emotional_change':'Recognition becomes shared ease','state_in':{'traveller':'Arrived and waving to friend'},'state_out':{'traveller':'Settled beside the waiting friend'}}
        p=compile_storyboard(raw,lyrics)
        self.assertEqual(p['scenes'][0]['story']['state_out']['traveller'],'Settled beside the waiting friend')
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

    def test_decorative_text_and_invisible_scale_are_repaired_without_relaxing_svg_validation(self):
        from song_animation.generative import normalize_package
        data={'assets':[{'id':'coin','svg':'<svg xmlns="http://www.w3.org/2000/svg"><circle r="10"/><text font-family="bad">$</text></svg>'}], 'nodes':[{'id':'head','keys':[{'t':0,'scale':0,'opacity':0},{'t':1,'scale':1,'opacity':1}]}]}
        result=normalize_package(data)
        sanitize_svg(result['assets'][0]['svg'])
        self.assertNotIn('<text',result['assets'][0]['svg'])
        self.assertEqual(result['nodes'][0]['keys'][0]['scale'],.05)
        self.assertEqual(data['nodes'][0]['keys'][0]['scale'],0)
        self.assertEqual(len(result['normalizations']),2)

    def test_parented_canvas_coordinates_are_detected_as_invisible(self):
        from song_animation.vector import invisible_foreground_nodes
        p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
        node=p['scenes'][0]['nodes'][2]
        node['parent']=p['scenes'][0]['nodes'][1]['id']
        for k in node['keys']:k.update(x=1500,y=2500)
        self.assertIn(node['id'],invisible_foreground_nodes(p))

    def test_changed_asset_becomes_variant_without_rewriting_previous_shots(self):
        from unittest.mock import patch
        from song_animation.generative import scene_package
        p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text());p['bible']={'style':'daylight'}
        for scene in p['scenes']:scene.update(visual=scene['label'],action='independent movement')
        previous=copy.deepcopy(p['assets']);aid=next(iter(previous));old=previous[aid]['svg']
        data={'background':p['scenes'][0]['background'],'assets':[dict(v,id=k) for k,v in p['assets'].items()],'nodes':copy.deepcopy(p['scenes'][0]['nodes'])}
        data['assets'][0]['svg']=old.replace('</svg>','<circle cx="8" cy="8" r="2" fill="#fff"/></svg>')
        with tempfile.TemporaryDirectory() as td,patch('song_animation.generative.generate_json',return_value=data):
            scene,assets=scene_package(p,0,td,previous)
        self.assertEqual(assets[aid]['svg'],old)
        self.assertTrue(any(k.startswith(aid+'_') for k in assets))
        self.assertTrue(scene['normalizations'])

    def test_quiet_independent_breathing_and_flicker_are_valid_motion(self):
        p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
        scene=p['scenes'][0];p['scenes']=[scene];p['total_frames']=scene['end_frame']
        for i,n in enumerate(scene['nodes']):
            n['wave']={};a=copy.deepcopy(n['keys'][0]);n['keys']=[dict(a,t=0),dict(a,t=.5,y=a.get('y',0)+2+i*.25),dict(a,t=1)]
        validate_vector(p)

    def test_missing_key_endpoints_hold_the_existing_poses(self):
        from song_animation.generative import normalize_package
        start={'t':.2,'x':10,'y':20,'opacity':0,'scale':1}
        end={'t':.8,'x':20,'y':30,'opacity':1,'scale':1}
        data=normalize_package({'nodes':[{'id':'note','keys':[start,end]}]})
        keys=data['nodes'][0]['keys']
        self.assertEqual([k['t'] for k in keys],[0,.2,.8,1])
        self.assertEqual(keys[0],dict(start,t=0))
        self.assertEqual(keys[-1],dict(end,t=1))

    def test_unreadable_rendered_motion_repairs_before_package_is_cached(self):
        from unittest.mock import patch
        from PIL import Image
        from song_animation.generative import scene_package
        from song_animation.vector import render_vector as real_render
        p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text());p['bible']={'style':'daylight'}
        for s in p['scenes']:s.update(visual=s['label'],action='independent movement')
        data={'background':p['scenes'][0]['background'],'assets':[dict(v,id=k) for k,v in p['assets'].items()],'nodes':p['scenes'][0]['nodes']}
        calls=[0]
        def sampled(plan,index,frame):
            calls[0]+=1
            return Image.new('RGB',(540,960),'white') if calls[0]<=3 else real_render(plan,index,frame)
        with tempfile.TemporaryDirectory() as td,patch('song_animation.generative.generate_json',return_value=data) as api,patch('song_animation.vector.render_vector',side_effect=sampled):
            scene,assets=scene_package(p,0,td,{})
            self.assertEqual(api.call_count,2)
            self.assertTrue(list((Path(td)/'vector_assets').glob('scene_*.json')))
