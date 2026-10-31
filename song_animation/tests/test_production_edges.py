import copy,json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from song_animation.quality import inspect_export

class AudioExportEdges(unittest.TestCase):
 def test_antiphase_stereo_is_compared_without_mono_cancellation(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);source=p/'source.wav';wrong=p/'wrong.wav';video=p/'film.mp4'
   subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','aevalsrc=0.1*sin(2*PI*440*t)|-0.1*sin(2*PI*440*t):s=44100:d=1',str(source)],check=True)
   subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','sine=frequency=880:duration=1',str(wrong)],check=True)
   subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=yellow:s=270x480:r=24:d=1','-i',str(source),'-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(video)],check=True)
   plan={'fps':24,'total_frames':24}
   self.assertTrue(inspect_export(video,source,plan,270)['passed'])
   self.assertFalse(inspect_export(video,wrong,plan,270)['passed'])
   self.assertIn('Wrong frame rate',inspect_export(video,source,{'fps':30,'total_frames':30},270)['reasons'])

 def test_silent_source_cannot_be_cleared_against_an_audible_export(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);audio=p/'silent.wav';video=p/'film.mp4'
   subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=44100:cl=stereo:d=1',str(audio)],check=True)
   subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=yellow:s=270x480:r=24:d=1','-f','lavfi','-i','sine=frequency=440:duration=1','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(video)],check=True)
   self.assertIn('Silent source was replaced with audible sound',inspect_export(video,audio,{'fps':24,'total_frames':24},270)['reasons'])

 def test_uploaded_video_without_audio_has_a_clear_input_error(self):
  from song_animation.clip import prepare
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);v=p/'silent_video.mp4'
   subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=blue:s=64x64:r=12:d=1','-an',str(v)],check=True)
   with self.assertRaisesRegex(ValueError,'no audio track'):prepare(v,p/'out')

class RecoveryEdges(unittest.TestCase):
 def test_model_discovery_outage_is_classified_as_provider_wait(self):
  import requests
  from song_animation.provider import generate_json,ProviderUnavailable
  with patch.dict('os.environ',{'GEMINI_API_KEY':'test-key'}),patch('requests.get',side_effect=requests.Timeout):
   with self.assertRaises(ProviderUnavailable):generate_json('unused')

 def test_corrupt_completion_record_is_not_treated_as_a_finished_song(self):
  from song_animation.completion import completed,source_hash
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);audio=root/'song.wav';audio.write_bytes(b'audio');records=root/'song_animation/completed';records.mkdir(parents=True)
   (records/(source_hash(audio)+'.json')).write_text('{broken')
   self.assertFalse(completed(root,audio))

 def test_cli_planning_stage_cannot_render_or_clear_a_video(self):
  from song_animation.run import main
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);lyrics=root/'given.json';lyrics.write_text('{"duration":2,"words":[]}');out=root/'out'
   with patch('sys.argv',['song','--audio','source','--out',str(out),'--lyrics',str(lyrics),'--stage','plan','--artwork','painted-layers']),patch('song_animation.run.prepare',return_value=('source',{'duration':2})),patch('song_animation.run.music_features',return_value={}),patch('song_animation.generative.build',return_value={'scenes':[]}),patch('song_animation.run.render') as render,patch('song_animation.environments.paint_environments') as paint:
    main();render.assert_not_called();paint.assert_not_called()
   self.assertEqual(json.loads((out/'status.json').read_text())['status'],'planned');self.assertFalse((out/'checked.mp4').exists())

 def test_provider_outage_does_not_download_asr_as_if_lyrics_were_wrong(self):
  from song_animation.audio_lyrics import analyze_audio
  from song_animation.provider import ProviderUnavailable
  with tempfile.TemporaryDirectory() as td,patch('song_animation.audio_lyrics.duration',return_value=3),patch('song_animation.audio_lyrics.subprocess.run'),patch('pathlib.Path.read_bytes',return_value=b'audio'),patch('song_animation.audio_lyrics.generate_json',side_effect=ProviderUnavailable([{'http_status':429,'retry_delay':'40000s'}])),patch('song_animation.recognition.recovery_evidence') as recovery:
   with self.assertRaises(ProviderUnavailable):analyze_audio('source',td)
   recovery.assert_not_called()

 def test_plan_only_stage_never_calls_asset_generator(self):
  from song_animation.generative import build
  from song_animation.tests.test_narrative import narrative
  with tempfile.TemporaryDirectory() as td,patch('song_animation.generative.storyboard',return_value={'scenes':narrative()['scenes'],'assets':{}}),patch('song_animation.generative.scene_package',side_effect=AssertionError('Painting before planning')) as art:
   result=build({'duration':6,'words':[]},{},td,artwork='painted-layers',plan_only=True)
   self.assertEqual(len(result['scenes']),3);art.assert_not_called()

 def test_attempt_flag_is_accepted_before_an_early_setup_failure(self):
  from song_animation.completion import main
  with tempfile.TemporaryDirectory() as td,patch('sys.argv',['completion','--audio','unused','--out',td,'--attempt']):main()

 def test_receipt_commit_retries_a_branch_race_without_force(self):
  from song_animation.completion import save_record
  session=Mock();session.get.return_value=Mock(status_code=404)
  session.put.side_effect=[Mock(status_code=409),Mock(status_code=201)]
  with patch('song_animation.completion.time.sleep'):
   save_record(session,'owner/repo','test-token','attempted',{'source_sha256':'a'*64,'status':'waiting_for_provider'})
  self.assertEqual(session.put.call_count,2)
  self.assertEqual(session.put.call_args.kwargs['json']['branch'],'main')

 def test_failed_song_is_rotated_behind_a_never_attempted_song(self):
  from song_animation.select_inputs import select
  from song_animation.completion import source_hash
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);inputs=root/'song_animation/inputs';inputs.mkdir(parents=True)
   (inputs/'a.wav').write_bytes(b'failed');(inputs/'b.wav').write_bytes(b'new')
   (root/'song_animation/queue_config.json').write_text('{"baseline_commit":"base"}')
   attempted=root/'song_animation/attempted';attempted.mkdir()
   (attempted/(source_hash(inputs/'a.wav')+'.json')).write_text('{"attempted_at":100}')
   diff=subprocess.CompletedProcess([],0,stdout=b'song_animation/inputs/a.wav\0song_animation/inputs/b.wav\0',stderr=b'')
   with patch('song_animation.select_inputs.subprocess.run',return_value=diff):self.assertEqual(select(root,event='schedule'),['song_animation/inputs/b.wav'])

class EnvironmentEdges(unittest.TestCase):
 def test_night_song_keeps_a_readable_night_setting(self):
  from song_animation.environments import environment_prompt
  prompt=environment_prompt({'allow_night':True},{'coverage':{'environment':'a moonlit village at night'}})
  self.assertIn('moonlight',prompt);self.assertNotIn('Bright daylight',prompt)

 def test_removing_background_layers_prunes_nested_empty_groups(self):
  from song_animation.environments import paint_environments,environment_prompt,cache_key
  from PIL import Image
  plan=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
  nodes=plan['scenes'][0]['nodes'];bg=nodes.pop(0)
  nodes[0]['id']='painted_environment'
  key=copy.deepcopy(bg['keys'])
  nodes[:0]=[dict(id='outer',asset=None,keys=key,role='background'),dict(id='inner',asset=None,parent='outer',keys=key,role='background'),dict(bg,id='bg',parent='inner')]
  with tempfile.TemporaryDirectory() as td:
   folder=Path(td)/'painted_environments';folder.mkdir()
   for s in plan['scenes']:Image.new('RGB',(512,896),'#b7d9de').save(folder/(cache_key(environment_prompt(plan,s))+'.png'))
   result=paint_environments(plan,td)
   ids=[n['id'] for n in result['scenes'][0]['nodes']]
   self.assertNotIn('outer',ids);self.assertNotIn('inner',ids);self.assertEqual(len(ids),len(set(ids)))
