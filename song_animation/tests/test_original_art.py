import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from song_animation.original_art import paint
from song_animation.provider import ProviderUnavailable
from song_animation.free_image import SPACE
from song_animation.local_image import compact_prompt

class OriginalArt(unittest.TestCase):
    def test_rejected_local_film_retries_remote_and_cannot_repeat_bad_cpu_fallback(self):
        from song_animation.original_art import reject_local_backend
        import hashlib
        with tempfile.TemporaryDirectory() as td:
            audio=Path(td,'clip.wav');audio.write_bytes(b'source')
            state=Path(td,'art_backend_choice.json')
            state.write_text(json.dumps({'source_clip_sha256':hashlib.sha256(b'source').hexdigest(),'backend':'cpu'}))
            reject_local_backend(td)
            with patch('song_animation.flux_layers.paint_foreground',side_effect=ProviderUnavailable([{'model':SPACE,'http_status':503}])) as remote,patch('song_animation.local_image.generate_image') as local:
                with self.assertRaises(ProviderUnavailable):paint({},td,audio)
                remote.assert_called_once_with({},Path(td))
                local.assert_not_called()
            with patch('song_animation.flux_layers.paint_foreground',return_value={'fresh':True}),patch('song_animation.flux_layers.paint_environments',return_value={'fresh':True}):
                self.assertEqual(paint({},td,audio),{'fresh':True})

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
        self.assertIn('Arms folded behind the back',rig)
        background=compact_prompt('Overhead close-up viewpoint. A balcony writing room. Background supporting this staging: A hand writes.')
        self.assertIn('supporting surface',background);self.assertNotIn('A hand writes',background)

class StoryOnlyHold(unittest.TestCase):
    def test_story_only_hold_does_not_ban_local_art_but_artwork_hold_does(self):
        from song_animation.original_art import reject_local_backend
        with tempfile.TemporaryDirectory() as td:
            state=Path(td,'art_backend_choice.json');state.write_text(json.dumps({'source_clip_sha256':'k','backend':'cpu'}))
            reject_local_backend(td,['No visually earned connected story/payoff','Story connection from shot 0 to 1 failed'])
            self.assertNotIn('visual_quality_rejected',json.loads(state.read_text()))
            reject_local_backend(td,['Artwork did not meet the stored finish reference'])
            self.assertTrue(json.loads(state.read_text())['visual_quality_rejected'])

class LocalPainterKeepsVectorPeople(unittest.TestCase):
    def test_cpu_backend_keeps_vector_figures_and_paints_objects(self):
        from song_animation import flux_layers
        svg='<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100" fill="#a55"/></svg>'
        plan={'assets':{'mother_hands':{'svg':svg,'width':100,'height':100,'description':'mother hands rolling roti'},
                        'brass_lota':{'svg':svg,'width':100,'height':100,'description':'brass lota pot','subject_kind':'object'}},
              'scenes':[{'nodes':[{'id':'a','asset':'mother_hands'},{'id':'b','asset':'brass_lota'}]}]}
        painted=[]
        with tempfile.TemporaryDirectory() as td,patch.object(flux_layers,'validate_vector',side_effect=lambda p:p),\
             patch.object(flux_layers,'prompt_for_asset',side_effect=lambda a,b,separate_limbs=False:painted.append(a['id']) or 'p'),\
             patch.object(flux_layers,'body_rig_asset',return_value=False),patch.object(flux_layers,'repair_context',return_value=''),\
             patch.object(flux_layers,'corrected_prompt',side_effect=lambda p,c:p),patch.object(flux_layers,'generate_image',side_effect=RuntimeError('stop')):
            with self.assertRaises(Exception):flux_layers.paint_foreground(plan,td,image_generator=flux_layers.generate_image,namespace='cpu-original-v1-x')
        self.assertEqual(painted,['brass_lota'])
