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
