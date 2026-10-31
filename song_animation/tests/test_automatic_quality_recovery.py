import copy,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from PIL import Image
from song_animation.quality import QualityHold
from song_animation.tests.test_quality_gate import clear_review

class AutomaticQualityRecovery(unittest.TestCase):
    def test_download_link_requires_a_real_checked_file_and_passed_status(self):
        from song_animation.status_summary import main
        import io
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);link='https://github.com/owner/repo/actions/runs/12/artifacts/34'
            with patch('sys.argv',['summary','--out',td]),patch.dict(os.environ,{'SONG_CHECKED_ARTIFACT_URL':link}):
                (out/'status.json').write_text(json.dumps({'status':'checks_passed'}))
                buffer=io.StringIO()
                with patch('sys.stdout',buffer):main()
                self.assertNotIn(link,buffer.getvalue())
                (out/'checked.mp4').write_bytes(b'checked video')
                buffer=io.StringIO()
                with patch('sys.stdout',buffer):main()
                self.assertIn(link,buffer.getvalue())
                (out/'status.json').write_text(json.dumps({'status':'blocked','automatic_repair_pending':True}))
                buffer=io.StringIO()
                with patch('sys.stdout',buffer):main()
                self.assertNotIn(link,buffer.getvalue());self.assertIn('अगली automatic कोशिश',buffer.getvalue())

    def test_later_attempt_repairs_failed_shots_without_restarting_the_story(self):
        from song_animation.run import main
        plan=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
        plan['scenes']=plan['scenes'][:1];plan['scenes'][0]['end_frame']=48;plan['total_frames']=48;plan['lyrics']=[]
        bad=clear_review();bad['shots'][0]['anatomy_continuity']=False
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);out=root/'out';out.mkdir();audio=root/'source.wav';audio.write_bytes(b'the same source clip')
            lyrics=root/'lyrics.json';lyrics.write_text(json.dumps({'duration':2,'words':[]}))
            def render(*a):
                (out/'preview.mp4').write_bytes(b'encoded draft')
                Image.new('RGB',(540,320),'beige').save(out/'review_contact.jpg')
            repaired=[]
            def refine(candidate,folder,assessment,**kwargs):
                repaired.append((kwargs['attempt_id'],copy.deepcopy(assessment['issues'])))
                return copy.deepcopy(candidate),True
            argv=['song','--audio',str(audio),'--out',str(out),'--lyrics',str(lyrics),'--artwork','vector']
            with patch('sys.argv',argv),patch('song_animation.run.prepare',return_value=(audio,{'duration':2})),patch('song_animation.run.music_features',return_value={}),patch('song_animation.generative.build',return_value=plan) as build,patch('song_animation.run.render',side_effect=render),patch('song_animation.review.review',side_effect=[bad,bad,bad,clear_review()]) as review,patch('song_animation.review.refine',side_effect=refine),patch('song_animation.run.inspect_export',return_value={'passed':True,'reasons':[]}):
                with patch.dict(os.environ,{'SONG_PRODUCTION_ATTEMPT':'job-A'}):
                    with self.assertRaises(QualityHold):main()
                    saved=json.loads((out/'pipeline_checkpoint.json').read_text())
                    self.assertEqual(saved['not_before_attempt'],'job-A');self.assertTrue(saved['pending_repair']);self.assertEqual(saved['pass_index'],1)
                    self.assertTrue(json.loads((out/'status.json').read_text())['automatic_repair_pending'])
                    self.assertFalse((out/'checked.mp4').exists());self.assertEqual(len(repaired),2)
                    with self.assertRaises(QualityHold):main()
                    self.assertEqual(len(repaired),2);self.assertEqual(review.call_count,3)
                with patch.dict(os.environ,{'SONG_PRODUCTION_ATTEMPT':'job-B'}):main()
                build.assert_called_once();self.assertEqual(len(repaired),3)
                self.assertEqual(repaired[-1][0],'job-B');self.assertTrue(all(i['shot']==0 for i in repaired[-1][1]))
                self.assertTrue((out/'checked.mp4').is_file());self.assertEqual(review.call_count,4)
                self.assertEqual(json.loads((out/'status.json').read_text())['status'],'checks_passed')

    def test_provider_retries_share_one_attempt_identity_but_new_jobs_do_not(self):
        from song_animation.resume import execute
        with tempfile.TemporaryDirectory() as td:
            identities=[]
            def run(cmd,env):
                identities.append(env['SONG_PRODUCTION_ATTEMPT'])
                if len(identities)==1:
                    Path(td,'status.json').write_text(json.dumps({'status':'waiting_for_provider','retryable':True}));return Mock(returncode=1)
                return Mock(returncode=0)
            with patch.dict(os.environ,{},clear=True),patch('song_animation.resume.subprocess.run',side_effect=run),patch('song_animation.resume.time.sleep'):
                self.assertEqual(execute(['--out',td]),0)
                self.assertEqual(execute(['--out',td]),0)
            self.assertEqual(identities[0],identities[1]);self.assertNotEqual(identities[1],identities[2])

    def test_new_repair_attempt_changes_image_request_even_if_defect_and_frames_match(self):
        from song_animation.review import refine
        from song_animation.flux_layers import repair_context
        p={'scenes':[{'nodes':[{'asset':'actor'}]}],'assets':{'actor':{}}}
        with tempfile.TemporaryDirectory() as td:
            Image.new('RGB',(540,320),'beige').save(Path(td,'review_contact.jpg'))
            def package(plan,index,out,assets,reference_image=None):return copy.deepcopy(plan['scenes'][index]),copy.deepcopy(assets)
            with patch('song_animation.generative.scene_package',side_effect=package),patch('song_animation.choreography.retarget',side_effect=lambda p,*a:(p,False)):
                a,_=refine(p,td,{'issues':[{'shot':0,'issue':'duplicate arm'}]},attempt_id='first-job')
                b,_=refine(p,td,{'issues':[{'shot':0,'issue':'duplicate arm'}]},attempt_id='next-job')
            self.assertNotEqual(repair_context(a,aid='actor'),repair_context(b,aid='actor'))

    def test_repeated_repairs_drop_abandoned_poses_and_keep_other_shots_assets(self):
        from song_animation.review import refine
        plan={'scenes':[{'nodes':[{'asset':'actor'}]},{'nodes':[{'asset':'friend'}]}],
              'assets':dict({'actor':{},'friend':{}},**{f'abandoned_pose_{i}':{} for i in range(180)})}
        def package(p,index,out,assets,reference_image=None):
            self.assertEqual(set(assets),{'actor','friend'})
            return dict(p['scenes'][index],nodes=[{'asset':'new_actor'}]),dict(assets,new_actor={})
        with tempfile.TemporaryDirectory() as td:
            Image.new('RGB',(540,640),'beige').save(Path(td,'review_contact.jpg'))
            with patch('song_animation.generative.scene_package',side_effect=package),patch('song_animation.choreography.retarget',side_effect=lambda p,*a:(p,False)):
                repaired,changed=refine(plan,td,{'issues':[{'shot':0,'issue':'wrong pose'}]},attempt_id='later-job')
            self.assertTrue(changed);self.assertEqual(set(repaired['assets']),{'new_actor','friend'})
            self.assertEqual(plan['scenes'][0]['nodes'][0]['asset'],'actor')
