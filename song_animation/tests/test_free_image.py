import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from PIL import Image
from song_animation.free_image import generate_image,SPACE
from song_animation.provider import ProviderUnavailable

class PublicImage(unittest.TestCase):
    def test_cached_verified_image_spends_no_gpu_requests(self):
        prompt='Original isolated subject';params={'space':SPACE,'prompt':prompt,'seed':12,'width':768,'height':1024,'steps':4}
        key=hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/(key+'.png');Image.new('RGB',(768,1024),'white').save(p)
            p.with_suffix('.json').write_text(json.dumps(dict(params,sha256=hashlib.sha256(p.read_bytes()).hexdigest())))
            with patch('requests.Session') as session:
                self.assertEqual(generate_image(prompt,td,12),p);session.assert_not_called()

    def test_http_quota_is_a_hold_not_an_unchecked_image(self):
        session=Mock();session.post.return_value=Mock(status_code=429)
        with tempfile.TemporaryDirectory() as td,patch('requests.Session',return_value=session):
            with self.assertRaises(ProviderUnavailable) as caught:generate_image('A subject',td,12)
            self.assertFalse(caught.exception.retryable);self.assertFalse(list(Path(td).glob('*.png')))

    def test_invalid_dimensions_are_rejected_before_network(self):
        with patch('requests.Session') as session:
            with self.assertRaises(ValueError):generate_image('A subject','unused',12,width=999999)
            session.assert_not_called()

    def test_prop_prompt_does_not_turn_warm_wood_into_a_person(self):
        from song_animation.flux_layers import prompt_for_asset
        p=prompt_for_asset({'id':'wooden_desk','description':'A warm wooden desk'}, {'characters':'A young poet'})
        self.assertNotIn('Character identity and clothing',p)
        p=prompt_for_asset({'id':'subject_hand','description':'A hand holding a pen'}, {'characters':'A young poet'})
        self.assertIn('ONLY the requested isolated hand',p)

    def test_nonhuman_heads_and_arms_keep_their_actual_subject_kind(self):
        from song_animation.flux_layers import prompt_for_asset
        for subject,kind in [('sunflower_head','plant'),('robot_arm','object')]:
            p=prompt_for_asset({'id':subject,'description':subject,'subject_kind':kind},{'characters':'A young poet'})
            self.assertNotIn('Character identity and clothing',p)
            self.assertNotIn('portrait head',p)
