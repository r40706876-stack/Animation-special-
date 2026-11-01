import unittest
from song_animation.pipeline_checkpoint import needs_scene_rewrite,ARTWORK_REVISION

class ArtworkRevision(unittest.TestCase):
    def test_old_raster_defects_are_repainted_before_ai_scene_rewrite(self):
        self.assertFalse(needs_scene_rewrite({'pending_repair':True},'flux-layers'))
        self.assertTrue(needs_scene_rewrite({'pending_repair':True,'artwork_revision':ARTWORK_REVISION},'flux-layers'))
    def test_unrelated_backends_and_clear_scenes_keep_recovery_behavior(self):
        self.assertTrue(needs_scene_rewrite({'pending_repair':True},'vector'))
        self.assertFalse(needs_scene_rewrite({'pending_repair':False},'flux-layers'))
        self.assertFalse(needs_scene_rewrite(None,'flux-layers'))
