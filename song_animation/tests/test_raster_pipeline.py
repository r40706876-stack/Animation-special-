"""Exercise real raster conversion, parenting, cache and encoded export together.

Only external image generation/matting is replaced with deterministic fixtures.
These are technical regression checks, not a visual quality certification.
"""
import copy,json,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image,ImageDraw
from song_animation.flux_layers import paint_foreground,paint_environments
from song_animation.vector import validate_vector,render_vector
from song_animation.render import render
from song_animation.quality import inspect_export

class RasterPipeline(unittest.TestCase):
    def plan(self):
        p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
        # A valid assetless parent was the production crash missed by unit tests.
        for s in p['scenes']:
            s['nodes'].insert(0,{'id':'group','asset':None,'keys':[{'t':0},{'t':1}]})
            s['nodes'][1]['parent']='group'
        return p

    def test_raster_conversion_group_cache_and_actual_audio_export(self):
        p=self.plan();original=copy.deepcopy(p);calls=[]
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            def image(prompt,out,seed,width=768,height=1024):
                calls.append(prompt);out=Path(out);out.mkdir(parents=True,exist_ok=True)
                path=out/(str(len(calls))+'.png')
                im=Image.new('RGBA',(width,height),'#fff4ce')
                ImageDraw.Draw(im).ellipse((width//4,height//4,width*3//4,height*3//4),fill='#3e8980')
                im.save(path);return path
            fake=types.SimpleNamespace(new_session=lambda *a,**k:object())
            with patch.dict(sys.modules,{'rembg':fake}),patch('song_animation.flux_layers.cutout',side_effect=lambda im,session:im.convert('RGBA')):
                first=paint_foreground(p,root,image_generator=image)
                count=len(calls)
                self.assertGreater(count,0)
                again=paint_foreground(p,root,image_generator=image)
                self.assertEqual(len(calls),count)
                self.assertEqual(first,again)
                painted=paint_environments(first,root,image_generator=image)
            self.assertEqual(p,original)
            validate_vector(painted)
            for i,s in enumerate(painted['scenes']):
                for f in (s['start_frame'],(s['start_frame']+s['end_frame'])//2,s['end_frame']-1):
                    self.assertEqual(render_vector(painted,i,f).size,(540,960))
            # Encode one second with real FFmpeg and compare the actual source audio.
            short=copy.deepcopy(painted);short['scenes']=short['scenes'][:1]
            short['scenes'][0]['end_frame']=short['fps'];short['total_frames']=short['fps']
            audio=root/'source.wav'
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','sine=frequency=330:duration=1',str(audio)],check=True)
            video=render(short,root/'export',audio,540)
            self.assertTrue(inspect_export(video,audio,short,540)['passed'])

    def test_invalid_plan_stops_before_any_image_call(self):
        p=self.plan();p['scenes'][0]['nodes'][-1]['asset']='missing_asset'
        with tempfile.TemporaryDirectory() as td,patch('song_animation.flux_layers.generate_image') as remote:
            with self.assertRaisesRegex(ValueError,'Missing custom asset'):
                paint_foreground(p,td)
            remote.assert_not_called()
