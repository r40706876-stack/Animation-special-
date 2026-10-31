import json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from song_animation.select_inputs import select

class UploadSelection(unittest.TestCase):
    def test_scheduled_retry_skips_cleared_source_and_picks_pending_upload(self):
        from song_animation.completion import source_hash
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);inputs=root/'song_animation/inputs';inputs.mkdir(parents=True)
            (inputs/'a.m4a').write_bytes(b'finished');(inputs/'b.m4a').write_bytes(b'pending')
            (root/'song_animation/queue_config.json').write_text(json.dumps({'baseline_commit':'baseline'}))
            done=root/'song_animation/completed';done.mkdir();sha=source_hash(inputs/'a.m4a')
            (done/(sha+'.json')).write_text(json.dumps({'status':'checks_passed','source_sha256':sha}))
            diff=subprocess.CompletedProcess([],0,stdout=b'song_animation/inputs/a.m4a\0song_animation/inputs/b.m4a\0',stderr=b'')
            with patch('song_animation.select_inputs.subprocess.run',return_value=diff):
                self.assertEqual(select(root,event='schedule'),['song_animation/inputs/b.m4a'])

    def test_draft_cannot_be_marked_complete(self):
        from song_animation.completion import receipt
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'status.json').write_text('{"status":"failed"}');(root/'quality_gate.json').write_text('{"passed":false}')
            with self.assertRaises(ValueError):receipt(root/'audio.m4a',root)

    def test_receipt_requires_the_actual_checked_video_hash(self):
        from song_animation.completion import receipt,source_hash
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);audio=root/'audio.m4a';audio.write_bytes(b'original audio');video=root/'checked.mp4';video.write_bytes(b'checked bytes')
            (root/'status.json').write_text('{"status":"checks_passed"}')
            clip=root/'source_clip.wav';clip.write_bytes(b'original excerpt')
            (root/'selection.json').write_text(json.dumps({'source_sha256':source_hash(audio),'start':0,'duration':2}))
            (root/'quality_gate.json').write_text(json.dumps({'passed':True,'technical':{'video_sha256':source_hash(video),'source_clip_sha256':source_hash(clip)}}))
            self.assertEqual(receipt(audio,root)['source_sha256'],source_hash(audio))
            video.write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError,'does not match'):receipt(audio,root)

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
