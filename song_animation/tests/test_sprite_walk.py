import base64,copy,io,json,unittest
from pathlib import Path
from PIL import Image
from song_animation.vector import validate_vector,render_vector

class IllustratedPoseCycle(unittest.TestCase):
    def plan(self):
        p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text());aid='kite';a=p['assets'][aid];frames=[]
        for color in ('red','blue','green'):
            stream=io.BytesIO();Image.new('RGBA',(int(a['width']),int(a['height'])),color).save(stream,format='PNG');frames.append(base64.b64encode(stream.getvalue()).decode())
        a.update(raster_png=frames[0],raster_frames=frames,frame_hold=3);return p
    def test_actual_render_uses_different_full_pose_frames(self):
        p=self.plan();self.assertNotEqual(render_vector(p,0,0).tobytes(),render_vector(p,0,3).tobytes())
    def test_mismatched_canvas_and_unbounded_cycle_are_rejected(self):
        p=self.plan();p['assets']['kite']['frame_hold']=0
        with self.assertRaisesRegex(ValueError,'pose cycle'):validate_vector(p)
        p=self.plan();p['assets']['kite']['raster_frames']*=5
        with self.assertRaisesRegex(ValueError,'pose cycle'):validate_vector(p)
        p=self.plan();stream=io.BytesIO();Image.new('RGBA',(5,6),'white').save(stream,format='PNG');p['assets']['kite']['raster_frames'][1]=base64.b64encode(stream.getvalue()).decode()
        with self.assertRaisesRegex(ValueError,'canvas'):validate_vector(p)

    def test_repainting_a_changed_asset_cannot_leave_an_old_pose_cycle_active(self):
        import tempfile,sys,types
        from unittest.mock import patch
        from song_animation.flux_layers import paint_foreground
        p=self.plan()
        with tempfile.TemporaryDirectory() as td:
            raw=Path(td)/'new.png';Image.new('RGBA',(100,100),'yellow').save(raw)
            fake=types.SimpleNamespace(new_session=lambda *a,**k:object())
            with patch.dict(sys.modules,{'rembg':fake}),patch('song_animation.flux_layers.cutout',side_effect=lambda im,s:im.convert('RGBA')):
                changed=paint_foreground(p,td,image_generator=lambda *a,**k:raw)
            self.assertNotIn('raster_frames',changed['assets']['kite'])
