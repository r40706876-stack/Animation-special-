import base64,copy,io,tempfile,unittest
from PIL import Image
from song_animation.coverage import validate_coverage,coverage_decision
from song_animation.vector import decode_painted,render_vector,validate_vector
from song_animation.environments import environment_prompt,cache_key,paint_environments
from song_animation.tests.test_quality_gate import clear_review
from song_animation.quality import visual_decision

def coverage():
    return [dict(coverage=dict(environment=['courtyard','courtyard','writing room','writing room','courtyard'][i],
        staging=['meeting near the fountain','a hesitant response','the first poem','the final blank line','a completed gesture'][i],
        framing='medium view',visible_event='A distinct visible action number '+str(i))) for i in range(5)]

class MultiScene(unittest.TestCase):
    def test_three_story_setups_are_accepted(self):validate_coverage(coverage(),30)
    def test_many_crops_of_one_desk_are_rejected(self):
        scenes=coverage()
        for i,s in enumerate(scenes):s['coverage'].update(environment='same desk',staging='same paper and hand',framing='zoom number '+str(i))
        with self.assertRaisesRegex(ValueError,'repeat one setup'):validate_coverage(scenes,30)
    def test_renaming_shots_does_not_override_actual_image_review(self):
        review=clear_review(5);review['visual_variety']=False
        self.assertFalse(visual_decision(review,5)['passed'])
    def test_missing_variety_evidence_cannot_clear_long_film(self):
        review=clear_review(5);review.pop('visual_variety',None)
        self.assertFalse(visual_decision(review,5)['passed'])
    def test_short_clip_is_not_forced_into_five_cuts(self):validate_coverage([{}],4)
    def test_set_cache_follows_song_world_but_not_camera_crop(self):
        p={'bible':{'palette':'cream and teal','locations':'sunlit courtyard'}}
        s=coverage()[0];a=environment_prompt(p,s);other=copy.deepcopy(s);other['coverage']['framing']='extreme closeup'
        self.assertEqual(cache_key(a),cache_key(environment_prompt(p,other)))
        other['coverage']['environment']='a snowy mountain'
        self.assertNotEqual(cache_key(a),cache_key(environment_prompt(p,other)))
        self.assertIn('no people',a)

class PaintedSafety(unittest.TestCase):
    def test_cached_painted_sets_preserve_foreground_actor_motion(self):
        import json
        from pathlib import Path
        plan=json.loads((Path(__file__).parents[1]/'examples'/'vector_smoke.json').read_text())
        before=[[copy.deepcopy(n) for n in s['nodes'] if n.get('role')!='background'] for s in plan['scenes']]
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)/'painted_environments';folder.mkdir()
            for s in plan['scenes']:Image.new('RGB',(512,896),'#b7d9de').save(folder/(cache_key(environment_prompt(plan,s))+'.png'))
            painted=paint_environments(plan,td)
            for i,s in enumerate(painted['scenes']):
                self.assertEqual([n for n in s['nodes'] if n.get('role')!='background'],before[i])
                self.assertTrue(s['nodes'][0]['painted_set'])
            # Decodes/composites the actual PNG, not a metadata-only assertion.
            im=render_vector(painted,0,2)
            self.assertEqual(im.size,(540,960));self.assertGreater(im.getpixel((0,0))[2],200)
            again=paint_environments(painted,td)
            self.assertEqual(sum(n.get('painted_set',False) for n in again['scenes'][0]['nodes']),1)

    def test_only_bounded_real_png_bytes_are_decoded(self):
        for s in ['https://example.com/image.png',base64.b64encode(b'<svg/>').decode(),'x'*4_000_001]:
            with self.assertRaises(ValueError):decode_painted(s)
        b=io.BytesIO();Image.new('RGB',(512,896),'#eacdb9').save(b,format='PNG')
        self.assertEqual(decode_painted(base64.b64encode(b.getvalue()).decode()).size,(512,896))

if __name__=='__main__':unittest.main()
