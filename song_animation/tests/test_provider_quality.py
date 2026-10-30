import os,unittest
from unittest.mock import patch,Mock
from song_animation.provider import generate_json
class QualityModelDiscovery(unittest.TestCase):
 def test_quality_request_can_use_discovered_pro_model(self):
  listing=Mock();listing.json.return_value={'models':[{'name':'models/gemini-2.5-pro','supportedGenerationMethods':['generateContent']},{'name':'models/gemini-3.5-flash-lite','supportedGenerationMethods':['generateContent']}]}
  response=Mock(status_code=200);response.json.return_value={'candidates':[{'content':{'parts':[{'text':'{"valid":true}'}]}}]}
  with patch.dict(os.environ,{'GEMINI_API_KEY':'test-key','GEMINI_MODEL':''}),patch('requests.get',return_value=listing),patch('requests.post',return_value=response) as post:
   self.assertTrue(generate_json('check actual words',prefer_quality=True)['valid'])
   self.assertIn('/gemini-2.5-pro:',post.call_args.args[0])

 def test_required_full_review_never_succeeds_using_lite_fallback(self):
  listing=Mock();listing.json.return_value={'models':[{'name':'models/'+m,'supportedGenerationMethods':['generateContent']} for m in ['gemini-2.5-pro','gemini-3.8-flash','gemini-2.5-flash','gemini-3.5-flash-lite']]}
  bad=Mock(status_code=429);good=Mock(status_code=200);good.json.return_value={'candidates':[{'content':{'parts':[{'text':'{"valid":true}'}]}}]}
  def post(url,**kwargs):return good if '/gemini-2.5-flash:' in url else bad
  with patch.dict(os.environ,{'GEMINI_API_KEY':'test-key','GEMINI_MODEL':''}),patch('requests.get',return_value=listing),patch('requests.post',side_effect=post) as api:
   result=generate_json('visual review',prefer_quality=True,require_full_model=True)
   self.assertEqual(result['_provider_model'],'gemini-2.5-flash')
   self.assertTrue(all('lite' not in c.args[0] for c in api.call_args_list))

 def test_live_verified_full_preview_is_preferred_over_unavailable_stable_names(self):
  listing=Mock();listing.json.return_value={'models':[{'name':'models/'+m,'supportedGenerationMethods':['generateContent']} for m in ['gemini-2.5-pro','gemini-3.8-flash','gemini-3-flash-preview','gemini-3.5-flash-lite']]}
  response=Mock(status_code=200);response.json.return_value={'candidates':[{'content':{'parts':[{'text':'{"valid":true}'}]}}]}
  with patch.dict(os.environ,{'GEMINI_API_KEY':'test-key','GEMINI_MODEL':''}),patch('requests.get',return_value=listing),patch('requests.post',return_value=response) as api:
   result=generate_json('meaning review',prefer_quality=True,require_full_model=True)
   self.assertEqual(result['_provider_model'],'gemini-3-flash-preview');self.assertEqual(api.call_count,1)
