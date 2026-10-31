import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from song_animation.provider import generate_json

class CompleteResponse(unittest.TestCase):
    def response(self,reason,text):
        r=Mock(status_code=200)
        r.json.return_value={'candidates':[{'finishReason':reason,'content':{'parts':[{'text':text}]}}],'usageMetadata':{'thoughtsTokenCount':30000}}
        return r

    def call(self,response,td,model='gemini-3-flash-preview'):
        listing=Mock();listing.json.return_value={'models':[{'name':'models/'+model,'supportedGenerationMethods':['generateContent']}]}
        with patch.dict(os.environ,{'GEMINI_API_KEY':'fake','GEMINI_MODEL':''}),patch('requests.get',return_value=listing),patch('requests.post',return_value=response) as api:
            data=generate_json('illustrate scene',out=td,thinking_level='low')
            return data,api.call_args.kwargs['json']['generationConfig']

    def test_token_cutoff_even_with_parseable_json_is_not_a_complete_package(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'MAX_TOKENS'):
                self.call(self.response('MAX_TOKENS','{"assets":[]}'),td)
            self.assertEqual(json.loads(Path(td,'planner_response_meta.json').read_text())['finish_reason'],'MAX_TOKENS')
            self.assertFalse(Path(td,'planner_raw.json').exists())

    def test_known_model_thinking_configuration_and_success(self):
        with tempfile.TemporaryDirectory() as td:
            data,config=self.call(self.response('STOP','{"assets":[]}'),td)
            self.assertEqual(config['thinkingConfig'],{'thinkingLevel':'low'})
            self.assertEqual(data['assets'],[])
        with tempfile.TemporaryDirectory() as td:
            _,config=self.call(self.response('STOP','{}'),td,'gemini-2.5-flash')
            self.assertEqual(config['thinkingConfig'],{'thinkingBudget':2048})
