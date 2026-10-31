import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from song_animation.original_art import paint
from song_animation.provider import ProviderUnavailable
from song_animation.free_image import SPACE
from song_animation.local_image import compact_prompt

class OriginalArt(unittest.TestCase):
    def test_source_switches_as_a_whole_and_does_not_retry_public_images_on_resume(self):
        with tempfile.TemporaryDirectory() as td:
            audio=Path(td,'clip.wav');audio.write_bytes(b'actual source clip');calls=[]
            def foreground(plan,out,**kwargs):
                calls.append(kwargs.get('namespace','flux'))
                if not kwargs:raise ProviderUnavailable([{'model':SPACE,'http_status':429}])
                return {'art':'local'}
            with patch('song_animation.flux_layers.paint_foreground',side_effect=foreground),patch('song_animation.flux_layers.paint_environments',return_value={'art':'local'}),patch('song_animation.local_image.generate_image'):
                self.assertEqual(paint({},td,audio),{'art':'local'})
                self.assertEqual(paint({},td,audio),{'art':'local'})
            self.assertEqual(calls[0],'flux');self.assertTrue(all(x.startswith('cpu-original') for x in calls[1:]))
            self.assertEqual(len(calls),3)

    def test_text_reviewer_outage_is_not_misreported_as_an_image_provider_outage(self):
        with tempfile.TemporaryDirectory() as td:
            audio=Path(td,'clip.wav');audio.write_bytes(b'actual source clip')
            with patch('song_animation.flux_layers.paint_foreground',side_effect=ProviderUnavailable([{'model':'gemini-model','http_status':503}])),patch('song_animation.local_image.generate_image') as local:
                with self.assertRaises(ProviderUnavailable):paint({},td,audio)
                local.assert_not_called()

    def test_local_prompts_keep_identity_and_closeup_perspective_in_short_context(self):
        prompt='A hand holding a pen. Premium detailed painterly illustration. Character identity and clothing: Indian poet with ivory sleeves and curly black hair. Palette: teal. Show ONLY the requested isolated hand with its cuff. One isolated subject.'
        short=compact_prompt(prompt)
        self.assertIn('ivory sleeves',short);self.assertIn('Only the requested isolated hand',short)
        rig=compact_prompt('Seated poet in a cream kurta. Premium detailed illustration. This is the head and torso of a layered animation rig: hands are hidden behind the body. Character identity and clothing: Indian poet. Palette: teal.')
        self.assertIn('no visible hands',rig)
        background=compact_prompt('Overhead close-up viewpoint. A balcony writing room. Background supporting this staging: A hand writes.')
        self.assertIn('supporting surface',background);self.assertNotIn('A hand writes',background)
