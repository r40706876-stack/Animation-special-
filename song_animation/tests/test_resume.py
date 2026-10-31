import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from song_animation.resume import execute
from song_animation.provider import ProviderUnavailable,generate_json

class Recovery(unittest.TestCase):
    def test_exhausted_model_is_skipped_on_the_next_wave(self):
        listing=Mock();listing.json.return_value={'models':[{'name':'models/'+m,'supportedGenerationMethods':['generateContent']} for m in ['gemini-3-flash-preview','gemini-3.5-flash']]}
        good=Mock(status_code=200);good.json.return_value={'candidates':[{'content':{'parts':[{'text':'{"valid":true}'}]}}]}
        with patch.dict(os.environ,{'GEMINI_API_KEY':'test-key','GEMINI_MODEL':'','SONG_PROVIDER_SKIP_MODELS':json.dumps(['gemini-3-flash-preview'])}),patch('requests.get',return_value=listing),patch('requests.post',return_value=good) as api:
            self.assertTrue(generate_json('continue saved scene',prefer_quality=True,require_full_model=True)['valid'])
            api.assert_called_once();self.assertIn('/gemini-3.5-flash:',api.call_args.args[0])

    def test_fourth_discovered_full_model_can_recover(self):
        listing=Mock();listing.json.return_value={'models':[{'name':'models/'+m,'supportedGenerationMethods':['generateContent']} for m in ['gemini-3-flash-preview','gemini-2.5-flash','gemini-3.5-flash','gemini-2.5-pro']]}
        good=Mock(status_code=200);good.json.return_value={'candidates':[{'content':{'parts':[{'text':'{"valid":true}'}]}}]}
        def post(url,**kwargs):return good if '/gemini-2.5-pro:' in url else Mock(status_code=503)
        with patch.dict(os.environ,{'GEMINI_API_KEY':'test-key','GEMINI_MODEL':''}),patch('requests.get',return_value=listing),patch('requests.post',side_effect=post) as api,patch('song_animation.provider.time.sleep'):
            self.assertTrue(generate_json('story review',prefer_quality=True,require_full_model=True)['valid'])
            self.assertEqual(api.call_count,5)

    def test_transient_service_is_distinct_from_quota_and_auth(self):
        self.assertTrue(ProviderUnavailable([{'model':'busy','http_status':503},{'model':'retired','http_status':404}]).retryable)
        mixed=ProviderUnavailable([{'model':'exhausted','http_status':429,'retry_delay':'43000s'},{'model':'busy','http_status':503}])
        self.assertTrue(mixed.retryable);self.assertEqual(mixed.blocked_models,['exhausted']);self.assertEqual(mixed.retry_after_seconds,0)
        self.assertFalse(ProviderUnavailable([{'model':'same','http_status':429},{'model':'same','http_status':503}]).retryable)
        self.assertFalse(ProviderUnavailable([{'http_status':401}]).retryable)

    def test_resume_keeps_arguments_and_stops_after_success(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);calls=[]
            def run(cmd,**kwargs):
                calls.append(cmd)
                if len(calls)==1:
                    (p/'status.json').write_text(json.dumps({'status':'waiting_for_provider','retryable':True,'blocked_models':['exhausted']}))
                    return Mock(returncode=1)
                self.assertEqual(json.loads(kwargs['env']['SONG_PROVIDER_SKIP_MODELS']),['exhausted'])
                return Mock(returncode=0)
            with patch('song_animation.resume.subprocess.run',side_effect=run),patch('song_animation.resume.time.sleep') as sleep:
                self.assertEqual(execute(['--audio','song.m4a','--out',td,'--stage','plan']),0)
                self.assertEqual(calls[0],calls[1]);sleep.assert_called_once_with(20)

    def test_quality_hold_quota_and_long_wait_are_not_retried(self):
        for status in ({'status':'blocked'},{'status':'waiting_for_provider','retryable':False},{'status':'waiting_for_provider','retryable':True,'retry_after_seconds':3600}):
            with self.subTest(status=status),tempfile.TemporaryDirectory() as td:
                def run(cmd,**kwargs):Path(td,'status.json').write_text(json.dumps(status));return Mock(returncode=1)
                with patch('song_animation.resume.subprocess.run',side_effect=run) as api,patch('song_animation.resume.time.sleep') as sleep:
                    self.assertEqual(execute(['--out',td]),1)
                    api.assert_called_once();sleep.assert_not_called()

    def test_repeated_busy_service_has_a_fixed_retry_limit(self):
        with tempfile.TemporaryDirectory() as td:
            def run(cmd,**kwargs):Path(td,'status.json').write_text(json.dumps({'status':'waiting_for_provider','retryable':True}));return Mock(returncode=1)
            with patch('song_animation.resume.subprocess.run',side_effect=run) as api,patch('song_animation.resume.time.sleep') as sleep:
                self.assertEqual(execute(['--out',td]),1)
                self.assertEqual(api.call_count,4);self.assertEqual(sleep.call_count,3)
