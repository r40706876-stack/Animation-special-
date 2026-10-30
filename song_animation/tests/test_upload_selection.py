import json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from song_animation.select_inputs import select

class UploadSelection(unittest.TestCase):
    def test_explicit_render_request_selects_the_existing_song_without_reupload(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);audio=root/'song_animation/inputs/my song.m4a';audio.parent.mkdir(parents=True);audio.write_bytes(b'audio')
            manifest=root/'song_animation/requests/retry.json';manifest.parent.mkdir();manifest.write_text(json.dumps({'audio_path':str(audio.relative_to(root))}))
            diff=subprocess.CompletedProcess([],0,stdout=b'song_animation/requests/retry.json\0',stderr=b'')
            with patch('song_animation.select_inputs.subprocess.run',return_value=diff):
                self.assertEqual(select(root,'before','head'),['song_animation/inputs/my song.m4a'])

    def test_wrong_branch_missing_file_has_actionable_error_and_no_substitute(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'Use main'):
                select(td,manual='song_animation/inputs/missing.m4a',event='workflow_dispatch')

    def test_request_cannot_escape_repository_or_select_a_non_audio_file(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaises(ValueError):select(root,manual='../outside.wav',event='workflow_dispatch')
            (root/'code.py').write_text('x=1')
            with self.assertRaises(ValueError):select(root,manual='code.py',event='workflow_dispatch')
