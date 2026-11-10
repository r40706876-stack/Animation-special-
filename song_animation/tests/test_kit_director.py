import unittest
from song_animation.kit.director import cut_shots,direct,keyword_compose,normalize
from song_animation.kit.art import OBJECTS

class KitDirector(unittest.TestCase):
    def test_shots_cover_clip_without_gaps(self):
        words=[{'start':0.2,'end':3,'text':'माँ'},{'start':3.2,'end':6,'text':'खेत'},{'start':12,'end':15,'text':'चाँद रात'}]
        shots=cut_shots(words,30.0)
        self.assertEqual(shots[0]['start'],0.0);self.assertEqual(shots[-1]['end'],30.0)
        for a,b in zip(shots,shots[1:]):self.assertAlmostEqual(a['end'],b['start'])
    def test_keywords_follow_the_lyric(self):
        self.assertIn('chulha',[o['name'] for o in keyword_compose('चूल्हे आगे माँ',0)['objects']])
        night=keyword_compose('रात चाँद तले',1);self.assertEqual(night['sky'],'night')
        self.assertNotIn('clock',[o['name'] for o in keyword_compose('पीपल की छाँव',2)['objects']])
    def test_model_output_is_clamped_to_vocabulary_and_bands(self):
        s=normalize({'setting':'outdoor','sky':'purple','objects':[{'name':'dragon','x':3,'y':-1},{'name':'tree','x':5,'y':.1,'scale':9}]},0)
        names=[o['name'] for o in s['objects']];self.assertEqual(names,['tree'])
        tree=s['objects'][0];self.assertTrue(.12<=tree['x']<=.88 and .62<=tree['y']<=.93 and tree['scale']<=1.5)
    def test_without_model_every_shot_is_composed(self):
        plan=direct([{'start':0,'end':4,'text':'कुछ भी'}],30.0,{},use_model=False)
        self.assertTrue(all(s['objects'] for s in plan['shots']))
        for s in plan['shots']:
            for o in s['objects']:self.assertTrue(o['name'] in OBJECTS or o['_pl']=='person')
