import copy,tempfile,unittest
from unittest.mock import patch
from song_animation.narrative import validate_story,narrative_decision
from song_animation.generative import compile_storyboard,storyboard
from song_animation.quality import visual_decision

def narrative():
 story={'premise':'A person notices a neighbour waiting','emotional_goal':'Turn distant admiration into a shared connection','opening':'Two people apart before a shared small gesture','turning_point':'A loose scarf brings the two into an interaction','payoff':'A returned scarf earns a shared smile','entities':{'pair':{'description':'Two neighbours wearing consistent clothes','initial_state':'Apart with no shared interaction'},'scarf':{'description':'One charcoal shawl with a bronze border','initial_state':'Held safely by its owner'}}}
 states=[{'pair':'One neighbour notices the other waiting','scarf':'A loose end slips into the breeze'},{'pair':'The neighbour reaches to help the owner','scarf':'The loose end is caught before falling'},{'pair':'Both neighbours smile after a shared gesture','scarf':'Returned to its owner and held safely'}]
 scenes=[];before={k:v['initial_state'] for k,v in story['entities'].items()}
 for i,after in enumerate(states):
  scenes.append({'start':i*2,'label':'A shared emotional story beat','visual':'The same neighbours and their charcoal scarf','action':'A connected gesture changes their relationship','lyric_ids':[],'story':{'purpose':['Establish the desire to connect','Create a helpful encounter','Resolve the earlier distance'][i],'link_from_previous':['Opening scene with both subjects','The earlier breeze creates the encounter','The caught scarf creates a shared response'][i],'emotional_change':['Distance becomes attention','Attention becomes care','Care becomes mutual recognition'][i],'state_in':copy.deepcopy(before),'state_out':copy.deepcopy(after)}})
  before=after
 return {'story':story,'bible':{'style':'warm bright illustration'},'scenes':scenes}

class ConnectedStory(unittest.TestCase):
 def test_connected_story_is_carried_into_render_plan(self):
  d=narrative();p=compile_storyboard(d,{'duration':6,'words':[]})
  self.assertEqual(p['story']['payoff'],d['story']['payoff'])
  self.assertEqual(p['scenes'][1]['story']['state_in'],p['scenes'][0]['story']['state_out'])
 def test_each_lyric_noun_as_unrelated_picture_is_rejected(self):
  d=narrative();d.pop('story')
  with self.assertRaisesRegex(ValueError,'connected story'):compile_storyboard(d,{'duration':6,'words':[]})
 def test_lost_prop_cannot_magically_reset_in_next_scene(self):
  d=narrative();d['scenes'][1]['story']['state_in']['scarf']='Held safely by its owner'
  with self.assertRaisesRegex(ValueError,'resets'):validate_story(d['story'],d['scenes'])
 def test_unchanged_portrait_or_camera_pan_is_not_story_progress(self):
  d=narrative();d['scenes'][0]['story']['state_out']=copy.deepcopy(d['scenes'][0]['story']['state_in'])
  with self.assertRaisesRegex(ValueError,'no story change'):validate_story(d['story'],d['scenes'])
 def test_subject_can_be_nonhuman_for_an_instrumental_song(self):
  story={'premise':'A seed reaches the morning light','emotional_goal':'Small growth becomes visible hope','opening':'A seed rests in a paper pot','turning_point':'Water reaches the waiting seed','payoff':'A shoot unfolds toward morning','entities':{'seed':{'description':'One small seed in the same paper pot','initial_state':'A dry seed waiting in soil'}}}
  scenes=[{'story':{'purpose':'Transform waiting into growth','link_from_previous':'Opening quiet moment in the pot','emotional_change':'Stillness becomes visible hope','state_in':{'seed':'A dry seed waiting in soil'},'state_out':{'seed':'A green shoot opens toward light'}}}]
  validate_story(story,scenes)
 def test_bad_story_is_automatically_replanned_before_assets(self):
  good=narrative();bad=copy.deepcopy(good);bad['scenes'][1]['story']['state_in']={}
  with tempfile.TemporaryDirectory() as td,patch('song_animation.generative.generate_json',side_effect=[bad,good,{'valid':True,'issues':[]}]) as api:
   result=storyboard({'duration':6,'words':[]},{},td)
   self.assertEqual(api.call_count,3);self.assertIn('STORY VALIDATION FAILED',api.call_args_list[1].args[0]);self.assertIn('story',result)
 def test_individually_pretty_frames_need_cross_shot_story_evidence(self):
  from song_animation.tests.test_quality_gate import clear_review
  review=clear_review(3);review['story_arc']=False
  self.assertFalse(visual_decision(review,3)['passed'])
 def test_transition_review_targets_the_actual_broken_link(self):
  from song_animation.tests.test_quality_gate import clear_review
  review=clear_review(3);review['story_links'][1]['state_continuity']=False
  reasons,repairs=narrative_decision(review,3)
  self.assertTrue(reasons);self.assertEqual(repairs[0]['shot'],2)

 def test_structurally_valid_but_emotionally_disconnected_plot_is_replanned(self):
  good=narrative()
  with tempfile.TemporaryDirectory() as td,patch('song_animation.generative.generate_json',side_effect=[good,{'valid':False,'issues':['No earned relationship change']},good,{'valid':True,'issues':[]}]) as api:
   result=storyboard({'duration':6,'words':[]},{},td)
   self.assertEqual(api.call_count,4);self.assertTrue(result['story_review']['valid'])
   self.assertIn('No earned relationship change',api.call_args_list[2].args[0])
