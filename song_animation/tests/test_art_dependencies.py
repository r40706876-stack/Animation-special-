import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from song_animation.art_dependencies import required

class ArtworkDependencies(unittest.TestCase):
    def test_exact_preserved_source_needs_neither_backend(self):
        p={'assets':{'figure':{'width':100,'height':200}},'scenes':[{'nodes':[{'asset':'figure'}]}]}
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);(out/'source_clip.wav').write_bytes(b'source');(out/'pipeline_checkpoint.json').write_text(json.dumps({'plan':p,'pending_repair':False}))
            with patch('song_animation.art_dependencies.apply',return_value=(p,{'figure'},{0})):
                r=required(out);self.assertFalse(r['needs_cpu']);self.assertFalse(r['needs_cutouts'])
    def test_rejected_cpu_is_not_installed_for_matching_source_but_other_source_is(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);(out/'source_clip.wav').write_bytes(b'source');(out/'art_backend_choice.json').write_text(json.dumps({'source_clip_sha256':hashlib.sha256(b'source').hexdigest(),'visual_quality_rejected':True,'rejection_reasons':['Artwork did not meet the stored finish reference']}))
            r=required(out);self.assertFalse(r['needs_cpu']);self.assertTrue(r['needs_cutouts'])
            (out/'source_clip.wav').write_bytes(b'other source');self.assertTrue(required(out)['needs_cpu'])
    def test_missing_cache_is_conservative(self):
        with tempfile.TemporaryDirectory() as td:self.assertTrue(required(td)['needs_cpu']);self.assertTrue(required(td)['needs_cutouts'])

class LegacyRejection(unittest.TestCase):
    def test_legacy_mark_without_reasons_installs_local_art_for_its_one_more_try(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);(out/'source_clip.wav').write_bytes(b'source');(out/'art_backend_choice.json').write_text(json.dumps({'source_clip_sha256':hashlib.sha256(b'source').hexdigest(),'visual_quality_rejected':True}))
            self.assertTrue(required(out)['needs_cpu'])
