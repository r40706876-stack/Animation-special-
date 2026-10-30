import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from song_animation.lyrics import shot_phrases
from song_animation.generative import scene_package
class LyricMeaning(unittest.TestCase):
 def test_shot_uses_actual_overlapping_words_instead_of_planner_label(self):
  p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text());p['bible']={'style':'daylight'}
  p['lyrics']=[{'start_frame':0,'end_frame':20,'text':'flowers caused these wounds'},{'start_frame':400,'end_frame':450,'text':'another distant line'}]
  for s in p['scenes']:s.update(visual='An unrelated standing person',action='an unrelated standing person')
  data={'background':p['scenes'][0]['background'],'assets':[dict(v,id=k) for k,v in p['assets'].items()],'nodes':p['scenes'][0]['nodes']}
  with tempfile.TemporaryDirectory() as td,patch('song_animation.generative.generate_json',return_value=data) as api:
   scene_package(p,0,td,{})
   prompt=api.call_args.args[0]
   self.assertIn('flowers caused these wounds',prompt)
   self.assertNotIn('another distant line',prompt)
 def test_instrumental_gap_does_not_inherit_previous_caption_meaning(self):
  p={'lyrics':[{'start_frame':0,'end_frame':20,'text':'a sung line'}]}
  self.assertEqual(shot_phrases(p,{'start_frame':20,'end_frame':40}),[])
