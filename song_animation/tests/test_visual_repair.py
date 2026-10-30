import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from song_animation.review import refine

class VisualRepair(unittest.TestCase):
    def test_actual_row_is_supplied_and_failed_repairs_preserve_original(self):
        original={'scenes':[{'label':'walk'},{'label':'shadow'}],'assets':{}}
        assessment={'issues':[{'shot':0,'issue':'missing feet'},{'shot':1,'issue':'missing shadow'},{'shot':99,'issue':'invalid index'}]}
        with tempfile.TemporaryDirectory() as td:
            Image.new('RGB',(540,640),'white').save(Path(td)/'review_contact.jpg')
            def package(plan,index,out,assets,reference_image=None):
                self.assertIn('inline_data',reference_image)
                self.assertIn('visual_correction',plan['scenes'][index])
                if index==1:raise ValueError('bad replacement')
                return dict(plan['scenes'][index],corrected=True),{'new_asset':{}}
            with patch('song_animation.generative.scene_package',side_effect=package) as api:
                result,changed=refine(original,td,assessment)
            self.assertTrue(changed);self.assertEqual(api.call_count,2)
            self.assertTrue(result['scenes'][0]['corrected'])
            self.assertEqual(result['scenes'][1],original['scenes'][1])
            self.assertNotIn('visual_correction',original['scenes'][0])
            report=json.loads((Path(td)/'visual_repair.json').read_text())
            self.assertEqual([x['status'] for x in report['results']],['replaced','failed'])
