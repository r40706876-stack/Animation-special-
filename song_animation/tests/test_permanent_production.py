import copy,json,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from song_animation.flux_layers import paint_foreground,paint_environments

FIXTURE=Path(__file__).parents[1]/'examples/vector_smoke.json'

class PermanentProduction(unittest.TestCase):
    def plan(self):
        p=json.loads(FIXTURE.read_text());p['bible']={'style':'Detailed warm painterly illustration','characters':'Consistent subjects'}
        for aid,a in p['assets'].items():a.update(id=aid,description=aid.replace('_',' '),subject_kind='object')
        return p

    def test_repair_regenerates_actual_bad_images_but_preserves_unaffected_assets(self):
        with tempfile.TemporaryDirectory() as td:
            calls=[]
            def image(prompt,out,seed,*args):
                calls.append((prompt,seed));path=Path(td)/f'raw_{len(calls)}.png'
                Image.new('RGB',(80,100),(len(calls)*21%255,90,150)).save(path);return path
            fake=types.SimpleNamespace(new_session=lambda *a,**k:object())
            with patch.dict(sys.modules,{'rembg':fake}),patch('song_animation.flux_layers.cutout',side_effect=lambda im,s:im.convert('RGBA')):
                plan=self.plan();plan['assets']['kite']['image_prompt']='A blue paper kite tilted upward with a long curved ribbon'
                original=paint_foreground(plan,td,image_generator=image);first=len(calls)
                self.assertTrue(any(p.startswith('A blue paper kite tilted upward') for p,s in calls))
                paint_foreground(plan,td,image_generator=image);self.assertEqual(len(calls),first)
                fixed=copy.deepcopy(original);fixed['scenes'][0]['visual_correction']={'issues':['Wrong subject pose'],'reference_sha256':'actual-visible-frames','pass':1}
                changed=paint_foreground(fixed,td,image_generator=image);after=len(calls)
                self.assertGreater(after,first)
                self.assertNotEqual(original['assets']['kite']['raster_png'],changed['assets']['kite']['raster_png'])
                self.assertEqual(original['assets']['lamp']['raster_png'],changed['assets']['lamp']['raster_png'])
                self.assertIn('Wrong subject pose',calls[-1][0])
                paint_foreground(fixed,td,image_generator=image);self.assertEqual(len(calls),after)
                fixed['scenes'][0]['visual_correction']['pass']=2
                paint_foreground(fixed,td,image_generator=image);self.assertGreater(len(calls),after)

    def test_viewpoint_and_visible_repair_reach_the_actual_background_generator(self):
        with tempfile.TemporaryDirectory() as td:
            calls=[]
            def image(prompt,*args):
                calls.append(prompt);p=Path(td)/'setting.png';Image.new('RGB',(270,480),'beige').save(p);return p
            plan=self.plan();s=plan['scenes'][0]
            s['coverage']={'framing':'overhead close-up','background_view':'A writing surface seen directly from above'}
            s['visual_correction']={'issues':['Wide window is wrong for an overhead desk shot'],'pass':1}
            paint_environments(plan,td,image_generator=image)
            self.assertIn('directly from above',calls[0]);self.assertIn('Wide window is wrong',calls[0])
            self.assertNotIn('REPAIR THE ACTUAL IMAGE',calls[1])

    def test_native_scene_can_correct_painted_view_without_changing_story_states(self):
        from song_animation.generative import scene_package
        plan=self.plan();plan['art_backend']='flux-layers';scene=plan['scenes'][0]
        scene['coverage']={'environment':'courtyard','staging':'a kite rises','framing':'wide'}
        scene['story']={'state_in':{'kite':'low'},'state_out':{'kite':'high'}}
        data={'background':scene['background'],'assets':list(plan['assets'].values()),'nodes':scene['nodes'],'background_view':'Look upward past the courtyard roof toward open sky'}
        with tempfile.TemporaryDirectory() as td,patch('song_animation.generative.generate_json',return_value=data) as api:
            result,_=scene_package(plan,0,td,{})
            self.assertEqual(result['coverage']['background_view'],data['background_view'])
            self.assertEqual(result['story'],scene['story'])
            self.assertGreaterEqual(len(api.call_args.kwargs['extra_parts']),2)

    def test_quality_reference_changes_invalidate_old_render_repair_checkpoints(self):
        from song_animation.pipeline_checkpoint import identity
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'source.wav';p.write_bytes(b'the same song')
            with patch('song_animation.film_standard.fingerprint',return_value='old-standard'):
                old=identity(p,{},'generated','flux-layers',1080)
            with patch('song_animation.film_standard.fingerprint',return_value='approved-film-standard'):
                self.assertNotEqual(old,identity(p,{},'generated','flux-layers',1080))

class EncodedDraftRecovery(unittest.TestCase):
    def test_retry_reuses_only_exact_plan_audio_and_unmodified_encoded_bytes(self):
        from song_animation.render import render
        plan=json.loads(FIXTURE.read_text());plan['scenes']=plan['scenes'][:1];plan['scenes'][0]['end_frame']=24;plan['total_frames']=24;plan['lyrics']=[]
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);video=render(plan,out,width=540);encoded=video.read_bytes();video.unlink()
            with patch('song_animation.render.render_frame',side_effect=AssertionError('Valid cached bytes should avoid re-rendering')):
                self.assertEqual(render(plan,out,width=540).read_bytes(),encoded)
            video.unlink();(out/'render_cache/preview.mp4').write_bytes(b'corrupt video')
            with patch('song_animation.render.render_frame',side_effect=RuntimeError('must regenerate damaged cached video')):
                with self.assertRaisesRegex(RuntimeError,'must regenerate'):render(plan,out,width=540)
            video=render(plan,out,width=540);video.unlink();changed=copy.deepcopy(plan);changed['scenes'][0]['background']='#ffbbbb'
            with patch('song_animation.render.render_frame',side_effect=RuntimeError('must regenerate changed composition')):
                with self.assertRaisesRegex(RuntimeError,'must regenerate'):render(changed,out,width=540)
            # Exact audio bytes are included even when the filename is unchanged.
            a=out/'audio.wav';a.write_bytes(b'first audio')
            from song_animation.render import digest
            first=digest(plan,a);a.write_bytes(b'different audio');self.assertNotEqual(first,digest(plan,a))
