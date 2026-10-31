import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from song_animation.illustration import illustrate
from song_animation.provider import ProviderUnavailable

SVG='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 120"><path d="M10 110 Q20 10 40 10 Q70 10 70 110Z" fill="#487b80"/></svg>'
ASSET={'id':'subject','width':80,'height':120,'description':'A small illustrated subject','svg':SVG}
GOOD={k:True for k in ('detail','anatomy_or_object_shape','subject_and_pose_preserved','reference_finish')};GOOD['issues']=[]

class Illustration(unittest.TestCase):
    def test_unsafe_generated_svg_is_not_rasterized_or_reviewed(self):
        with tempfile.TemporaryDirectory() as td,patch('song_animation.illustration.generate_json',return_value={'svg':'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'}) as api:
            with self.assertRaises(ValueError):illustrate(ASSET,{},td)
            api.assert_called_once()

    def test_failed_finish_review_blocks_the_asset(self):
        bad=dict(GOOD,detail=False,issues=['Blank face and geometric body'])
        with tempfile.TemporaryDirectory() as td,patch('song_animation.illustration.generate_json',side_effect=[{'svg':SVG},bad,{'svg':SVG},bad]):
            with self.assertRaisesRegex(ValueError,'expensive film rendering blocked'):illustrate(ASSET,{},td)
            self.assertFalse(Path(td,'asset.json').exists())

    def test_review_outage_keeps_completed_drawing_for_resume(self):
        with tempfile.TemporaryDirectory() as td:
            with patch('song_animation.illustration.generate_json',side_effect=[{'svg':SVG},ProviderUnavailable([{'model':'busy','http_status':503}])]):
                with self.assertRaises(ProviderUnavailable):illustrate(ASSET,{},td)
            with patch('song_animation.illustration.generate_json',return_value=GOOD) as api:
                asset=illustrate(ASSET,{},td)
                api.assert_called_once();self.assertEqual((asset['width'],asset['height']),(80,120))
