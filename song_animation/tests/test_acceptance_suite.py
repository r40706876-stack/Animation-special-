import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from song_animation.acceptance_suite import cases,run,assess

class RealInputAcceptance(unittest.TestCase):
    def setup_suite(self,root):
        inputs=root/'song_animation/inputs';inputs.mkdir(parents=True)
        paths=[]
        for i in range(3):
            p=inputs/(str(i)+'.wav');p.write_bytes(('distinct source '+str(i)).encode());paths.append(str(p.relative_to(root)))
        manifest=root/'manifest.json';manifest.write_text(json.dumps({'audio_paths':paths}))
        return manifest,paths

    def test_renamed_same_audio_does_not_count_as_a_different_song(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);manifest,paths=self.setup_suite(root)
            (root/paths[1]).write_bytes((root/paths[0]).read_bytes())
            with self.assertRaisesRegex(ValueError,'different audio bytes'):cases(root,manifest)

    def test_provider_hold_defers_remaining_inputs_and_cannot_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);manifest,_=self.setup_suite(root);out=root/'out'
            def launch(*args,**kwargs):
                argv=args[0];folder=Path(argv[argv.index('--out')+1]);folder.mkdir(exist_ok=True)
                (folder/'status.json').write_text('{"status":"waiting_for_provider","retry_after_seconds":3600}')
                self.assertEqual(kwargs['env']['SONG_ACCEPTANCE_COLD_START'],'1')
                return Mock(wait=Mock(return_value=1))
            with patch('song_animation.acceptance_suite.subprocess.Popen',side_effect=launch) as start:
                self.assertEqual(run(root,manifest,out),1)
                self.assertEqual(start.call_count,1)
            report=json.loads((out/'acceptance_report.json').read_text())
            self.assertFalse(report['passed']);self.assertEqual(len(report['cases']),3)
            self.assertEqual(report['cases'][2]['production_status'],'deferred_provider_cooldown')

    def test_green_metadata_without_actual_export_and_reviews_does_not_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);audio=root/'a.wav';audio.write_bytes(b'source')
            (root/'status.json').write_text('{"status":"checks_passed"}')
            (root/'quality_gate.json').write_text('{"passed":true}')
            self.assertFalse(assess(audio,root)['passed'])

    def test_cold_start_disables_handwritten_lyrics_and_source_art(self):
        from song_animation.run import cached_reference
        from song_animation.source_art import apply
        with patch.dict('os.environ',{'SONG_ACCEPTANCE_COLD_START':'1'}):
            self.assertIsNone(cached_reference('unused',{'start':0}))
            plan={'scenes':[]}
            self.assertEqual(apply(plan,'a'*64),(plan,set(),set()))

    def test_resume_keeps_provider_cooldown_without_starting_a_new_job(self):
        import time
        from song_animation.acceptance_suite import sha
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);manifest,paths=self.setup_suite(root);out=root/'out';folder=out/'0-0';folder.mkdir(parents=True)
            (folder/'acceptance_origin.json').write_text(json.dumps({'source_sha256':sha(root/paths[0]),'manual_source_art_allowed':False,'generation_commit':'prior'}))
            deadline=time.time()+3600
            (folder/'acceptance_case.json').write_text(json.dumps({'passed':False,'retry_not_before':deadline}))
            with patch('song_animation.acceptance_suite.subprocess.Popen') as launch:
                self.assertEqual(run(root,manifest,out),1)
                launch.assert_not_called()
            self.assertEqual(json.loads((folder/'acceptance_case.json').read_text())['retry_not_before'],deadline)

    def test_previously_cleared_outputs_are_rechecked_and_not_regenerated(self):
        from song_animation.acceptance_suite import sha
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);manifest,paths=self.setup_suite(root);out=root/'out'
            for i,path in enumerate(paths):
                folder=out/(str(i)+'-'+Path(path).stem);folder.mkdir(parents=True)
                (folder/'acceptance_origin.json').write_text(json.dumps({'source_sha256':sha(root/path),'manual_source_art_allowed':False,'generation_commit':'prior'}))
                (folder/'acceptance_case.json').write_text(json.dumps({'passed':True,'source_sha256':sha(root/path)}))
            with patch('song_animation.acceptance_suite.assess',return_value={'passed':True}) as check,patch('song_animation.acceptance_suite.subprocess.Popen') as launch:
                self.assertEqual(run(root,manifest,out),0);self.assertEqual(check.call_count,3);launch.assert_not_called()
            self.assertTrue(json.loads((out/'acceptance_report.json').read_text())['passed'])
