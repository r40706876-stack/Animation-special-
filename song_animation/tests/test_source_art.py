import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from PIL import Image
from song_animation.source_art import apply,fingerprint,scene_fingerprint

class SourceBoundArt(unittest.TestCase):
    def test_exact_source_plan_and_bytes_are_required_and_pose_patch_is_preserved(self):
        p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
        with tempfile.TemporaryDirectory() as td:
            source='a'*64;folder=Path(td)/source;folder.mkdir();aid='kite';file=folder/'kite.png';Image.new('RGBA',(80,100),'blue').save(file)
            item={'file':'kite.png','sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'width':80,'height':100,'provider':'original asset'}
            manifest={'source_clip_sha256':source,'plan_fingerprints':[fingerprint(p)],'assets':{aid:item},'scene_fingerprints':{'0':[scene_fingerprint(p['scenes'][0])]},'scenes':[{'index':0,'nodes':p['scenes'][0]['nodes']}]}
            (folder/'manifest.json').write_text(json.dumps(manifest));fixed,locked,scenes=apply(p,source,td)
            self.assertEqual(locked,{aid});self.assertEqual(scenes,{0});self.assertIn('raster_png',fixed['assets'][aid]);self.assertNotIn('raster_png',p['assets'][aid])
            self.assertEqual(apply(p,'b'*64,td),(p,set(),set()))
            changed=copy.deepcopy(p);changed['scenes'][0]['label']='different shot';self.assertEqual(apply(changed,source,td),(changed,set(),set()))
            unrelated=copy.deepcopy(p);unrelated['scenes'][1]['label']='other scene repair'
            self.assertEqual(apply(unrelated,source,td)[1],{aid})
            file.write_bytes(b'changed bytes')
            with self.assertRaisesRegex(ValueError,'bytes changed'):apply(p,source,td)
    def test_preserved_source_assets_are_not_sent_to_an_image_provider(self):
        import sys,types
        from unittest.mock import patch
        from song_animation.flux_layers import paint_foreground
        p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
        active={n.get('asset') for s in p['scenes'] for n in s['nodes'] if n.get('asset')}
        with tempfile.TemporaryDirectory() as td,patch.dict(sys.modules,{'rembg':types.SimpleNamespace(new_session=lambda **k:None)}),patch('song_animation.flux_layers.generate_image',side_effect=AssertionError('Provider must not repaint locked source assets')):
            def forbidden(*a,**k):raise AssertionError('Provider must not repaint locked source assets')
            self.assertEqual(paint_foreground(p,td,image_generator=forbidden,preserved_assets=active),p)

    def test_one_changed_scene_keeps_other_scene_art_without_overwriting_shared_repair(self):
        p=json.loads((Path(__file__).parents[1]/'examples/vector_smoke.json').read_text())
        p['scenes'][1]['nodes'][-1]['asset']='kite'
        with tempfile.TemporaryDirectory() as td:
            source='c'*64;folder=Path(td)/source;folder.mkdir();file=folder/'kite.png';Image.new('RGBA',(80,100),'blue').save(file)
            item={'file':'kite.png','sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'width':80,'height':100,'provider':'original art'}
            manifest={'source_clip_sha256':source,'assets':{'kite':item},'scene_fingerprints':{str(i):[scene_fingerprint(p['scenes'][i])] for i in (0,1)},'scenes':[{'index':i,'nodes':p['scenes'][i]['nodes']} for i in (0,1)]}
            (folder/'manifest.json').write_text(json.dumps(manifest))
            p['scenes'][1]['label']='new repaired staging'
            fixed,locked,scenes=apply(p,source,td)
            alias=next(iter(locked));self.assertNotEqual(alias,'kite');self.assertEqual(scenes,{0})
            self.assertEqual(fixed['scenes'][0]['nodes'][1]['asset'],alias)
            self.assertEqual(fixed['scenes'][1]['nodes'][-1]['asset'],'kite')
            self.assertNotIn('raster_png',fixed['assets']['kite'])
            resumed,locked2,scenes2=apply(fixed,source,td)
            self.assertEqual(locked2,locked);self.assertEqual(scenes2,scenes)
