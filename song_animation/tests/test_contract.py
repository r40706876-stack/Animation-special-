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
