import copy,json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from song_animation.quality import CHECKS,QualityHold,visual_decision,inspect_export
from song_animation.recognition import consistent_matches

def clear_review(n=1):
 return {'visual_variety':True,'story_arc':True,'story_links':[{'from':i,'to':i+1,'causal_connection':True,'state_continuity':True,'emotional_progression':True} for i in range(n-1)],'needs_review':False,'issues':[],'reviewer_model':'gemini-quality-pro','reference_quality_met':True,'shots':[dict(shot=i,**{k:True for k in CHECKS}) for i in range(n)]}
class OutputPolicy(unittest.TestCase):
 def test_old_empty_advisory_review_cannot_clear_film(self):
  self.assertFalse(visual_decision({'needs_review':False,'issues':[]},1)['passed'])
 def test_unavailable_review_cannot_clear_film(self):
  self.assertFalse(visual_decision({'status':'unavailable'},1)['passed'])
 def test_lite_cannot_clear_even_with_all_positive_flags(self):
  r=clear_review();r['reviewer_model']='gemini-flash-lite'
  self.assertFalse(visual_decision(r,1)['passed'])
 def test_all_scenes_and_explicit_booleans_required(self):
  a=clear_review(2);a['shots'][1]['lyric_meaning']='true'
  self.assertFalse(visual_decision(a,2)['passed'])
  a=clear_review(2);a['shots'][1]['shot']=0
  self.assertFalse(visual_decision(a,2)['passed'])
 def test_false_art_or_motion_produces_targeted_repairs(self):
  a=clear_review();a['shots'][0]['story_motion']=False;a['shots'][0]['reason']='Only background particles move'
  d=visual_decision(a,1);self.assertFalse(d['passed']);self.assertEqual(d['repair_issues'][0]['shot'],0)
  self.assertIn('story_motion',d['repair_issues'][0]['issue'])
 def test_complete_explicit_evidence_clears_automated_visual_checks(self):
  self.assertTrue(visual_decision(clear_review(3),3)['passed'])
 def exercise(self,reviews,technical=None,repair=True):
  from song_animation.run import main
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/'out';out.mkdir();(out/'checked.mp4').write_bytes(b'stale');(out/'preview.mp4').write_bytes(b'stale draft')
   lyrics=Path(td)/'given.json';lyrics.write_text(json.dumps({'duration':2,'words':[]}))
   plan={'fps':24,'total_frames':48,'scenes':[{}]}
   def draw(*args):(out/'preview.mp4').write_bytes(b'new draft')
   with patch('sys.argv',['song','--audio','source','--out',str(out),'--lyrics',str(lyrics)]),patch('song_animation.run.prepare',return_value=('source',{'duration':2})),patch('song_animation.run.music_features',return_value={}),patch('song_animation.generative.build',return_value=plan),patch('song_animation.run.render',side_effect=draw) as rendered,patch('song_animation.review.review',side_effect=reviews),patch('song_animation.review.refine',return_value=(plan,repair)) as refine,patch('song_animation.run.inspect_export',return_value=technical or {'passed':True,'reasons':[]}):
    try:main()
    except QualityHold:pass
    return json.loads((out/'status.json').read_text()),(out/'checked.mp4').exists(),rendered.call_count,refine.call_count
 def test_missing_review_removes_stale_success_file(self):
  status,exists,_,_=self.exercise([{'status':'unavailable'}]);self.assertEqual(status['status'],'blocked');self.assertFalse(exists)
 def test_bad_shot_is_automatically_rerendered_and_rechecked(self):
  bad=clear_review();bad['shots'][0]['lyric_meaning']=False
  status,exists,renders,repairs=self.exercise([bad,clear_review()]);self.assertEqual(status['status'],'checks_passed');self.assertTrue(exists);self.assertEqual((renders,repairs),(2,1))
 def test_two_failed_repair_passes_never_create_checked_file(self):
  bad=clear_review();bad['shots'][0]['artwork_detail']=False
  status,exists,renders,repairs=self.exercise([bad,bad,bad]);self.assertFalse(exists);self.assertEqual(status['status'],'blocked');self.assertEqual((renders,repairs),(3,2))
 def test_technical_failure_overrides_positive_ai_review(self):
  status,exists,_,_=self.exercise([clear_review()],{'passed':False,'reasons':['Wrong audio']});self.assertFalse(exists);self.assertEqual(status['status'],'blocked')

class AudioIdentity(unittest.TestCase):
 def candidate(self,offset,key='10'):
  return {'track':{'key':key,'title':'Actual title'},'matches':[{'id':key,'offset':offset}]}
 def test_same_name_without_consistent_offsets_is_not_accepted(self):
  self.assertIsNone(consistent_matches([self.candidate(5),self.candidate(25)],[0,3]))
 def test_disagreeing_tracks_are_not_accepted(self):
  self.assertIsNone(consistent_matches([self.candidate(5),self.candidate(8,'11')],[0,3]))
 def test_two_consistent_windows_provide_hint_not_lyric_certificate(self):
  d=consistent_matches([self.candidate(47.4),self.candidate(50.4)],[0,3]);self.assertEqual(d['title'],'Actual title');self.assertFalse(d['lyric_verified'])

class RealEncodedExport(unittest.TestCase):
 def test_actual_mp4_frames_and_original_audio_are_inspected(self):
  from song_animation.review import encoded_sample
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);audio=p/'sound.wav';video=p/'movie.mp4';wrong=p/'wrong.wav'
   subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','sine=frequency=440:duration=1',str(audio)],check=True)
   subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','sine=frequency=880:duration=1',str(wrong)],check=True)
   subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=red:s=270x480:r=24:d=1','-i',str(audio),'-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(video)],check=True)
   pixel=encoded_sample(video,.5).getpixel((200,200));self.assertGreater(pixel[0],220);self.assertLess(pixel[2],20)
   self.assertTrue(inspect_export(video,audio,{'fps':24,'total_frames':24},270)['passed'])
   self.assertFalse(inspect_export(video,wrong,{'fps':24,'total_frames':24},270)['passed'])
