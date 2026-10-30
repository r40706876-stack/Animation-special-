import copy,json,unittest
from pathlib import Path
from song_animation.contract import validate,validate_lyrics
from song_animation.director import compile_plan
from song_animation.art import render_frame
class Contracts(unittest.TestCase):
    def setUp(self):self.p=json.loads((Path(__file__).parents[1]/'examples/proof.json').read_text())
    def test_gap_and_overlap_rejected(self):
        for delta in (-1,1):
            p=copy.deepcopy(self.p);p['scenes'][1]['start_frame']+=delta
            with self.assertRaises(ValueError):validate(p)
    def test_no_generic_action_fallback(self):
        self.p['scenes'][0]['kind']='fly'
        with self.assertRaises(ValueError):validate(self.p)
    def test_actual_word_timing_preserved(self):
        lyrics={'duration':8.,'words':[{'text':'a','start':0.,'end':3.},{'text':'b','start':4.,'end':5.},{'text':'c','start':6.,'end':7.}]}
        data={'palette':'warm','scenes':[{'kind':'gift','start_word_id':0,'cue_word_id':0,'lyric_ids':[0],'reason':'gift'},{'kind':'heart','start_word_id':1,'cue_word_id':2,'lyric_ids':[1,2],'reason':'memory'}]}
        p=compile_plan(data,lyrics);self.assertEqual(p['scenes'][1]['start_frame'],96);self.assertEqual(p['scenes'][1]['cue_frame'],144)
    def test_omitted_words_rejected(self):
        with self.assertRaises(ValueError):compile_plan({'palette':'warm','scenes':[{'kind':'gift','start_word_id':0,'cue_word_id':0,'lyric_ids':[],'reason':'gift'}]}, {'duration':5,'words':[{'start':0,'end':2,'text':'a'}]})
    def test_out_of_bounds_lyrics_rejected(self):
        with self.assertRaises(ValueError):validate_lyrics([{'start':-1,'end':2,'text':'x'}],3)
    def test_portal_matches_next_scene(self):
        end=self.p['scenes'][1]['end_frame'];self.assertEqual(render_frame(self.p,end-1).tobytes(),render_frame(self.p,end).tobytes())
    def test_deterministic_render(self):self.assertEqual(render_frame(self.p,230).tobytes(),render_frame(self.p,230).tobytes())
if __name__=='__main__':unittest.main()

class LocalDirector(unittest.TestCase):
    def test_untranscribed_opening_is_not_visualized_as_known_lyrics(self):
        from song_animation.local_director import local_plan
        with self.assertRaisesRegex(ValueError,'Untranscribed opening'):
            local_plan({'duration':15,'words':[{'text':'दिल फूल','start':8,'end':10}]})
    def test_supported_phrases_cover_words_and_show_planner_identity(self):
        from song_animation.local_director import local_plan
        words=[{'text':t,'start':i*1.,'end':i+0.8} for i,t in enumerate(['दिल','ज़ख्म,','फूल','चोट,','अपने','दूर'])]
        p=local_plan({'duration':7,'words':words})
        self.assertEqual(p['planner'],'local_rules')
        self.assertEqual([i for s in p['scenes'] for i in s['lyric_ids']],list(range(6)))
    def test_unrelated_song_needs_other_assets(self):
        from song_animation.local_director import local_plan
        with self.assertRaises(ValueError):local_plan({'duration':4,'words':[{'text':'पहाड़ नदी मौसम','start':0,'end':3}]})

class InputSelection(unittest.TestCase):
    def test_manual_path_must_be_inside_repository(self):
        import tempfile
        from song_animation.select_inputs import select
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):select(td,manual='../outside.mp3',event='workflow_dispatch')
    def test_changed_uploads_are_each_selected_instead_of_old_reference(self):
        import tempfile,subprocess
        from song_animation.select_inputs import select
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);folder=root/'song_animation/inputs';folder.mkdir(parents=True)
            (folder/'reference.mp3').write_bytes(b'ref')
            def git(*args):return subprocess.check_output(['git',*args],cwd=root).decode().strip()
            git('init','-q');git('config','user.email','test@example.invalid');git('config','user.name','test')
            git('add','.');git('commit','-qm','base');before=git('rev-parse','HEAD')
            for name in ('first song.mp3','second.wav'):(folder/name).write_bytes(b'audio')
            git('add','.');git('commit','-qm','upload');head=git('rev-parse','HEAD')
            self.assertEqual(select(root,before,head),['song_animation/inputs/first song.mp3','song_animation/inputs/second.wav'])

class PhraseTiming(unittest.TestCase):
    def test_explicit_instrumental_tail_is_not_extended_lyric_shot(self):
        lyrics={'duration':12,'timing_granularity':'phrase','instrumental':[{'start':8,'end':12}], 'words':[{'text':'दिल पर जख्म','start':0,'end':4},{'text':'अपने दूर','start':4,'end':8}]}
        raw={'palette':'memory','scenes':[{'kind':'wounded_heart','start_word_id':0,'cue_word_id':0,'lyric_ids':[0],'reason':'pain'},{'kind':'paths','start_word_id':1,'cue_word_id':1,'lyric_ids':[1],'reason':'distance'}]}
        p=compile_plan(raw,lyrics)
        self.assertEqual(p['scenes'][-1]['lyric_ids'],[])
        self.assertEqual(p['scenes'][-1]['start_frame'],192)
        self.assertEqual(p['cue_method'],'art-directed emphasis within timed phrases')

class Continuity(unittest.TestCase):
    def test_heart_retains_wounds_from_previous_shot(self):
        from PIL import ImageChops
        base={'version':1,'fps':24,'palette':'memory','total_frames':192,'scenes':[{'kind':'wounded_heart','start_frame':0,'end_frame':96,'cue_frame':50,'lyric_ids':[],'reason':'wounds'},{'kind':'heart','start_frame':96,'end_frame':192,'cue_frame':145,'lyric_ids':[],'reason':'memory'}]}
        wounded=render_frame(base,96)
        base['scenes'][0]['kind']='gift'
        fresh=render_frame(base,96)
        self.assertIsNotNone(ImageChops.difference(wounded.crop((160,350,370,610)),fresh.crop((160,350,370,610))).getbbox())
