import json,tempfile,unittest
from pathlib import Path
from song_animation.completion import retry_ready,source_hash

class ProviderCooldown(unittest.TestCase):
    def test_server_deadline_survives_between_independent_queue_runs(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);audio=root/'song.wav';audio.write_bytes(b'song')
            records=root/'song_animation/attempted';records.mkdir(parents=True)
            p=records/(source_hash(audio)+'.json')
            p.write_text(json.dumps({'status':'waiting_for_provider','retry_not_before':5000}))
            self.assertFalse(retry_ready(root,audio,now=4999))
            self.assertTrue(retry_ready(root,audio,now=5000))
            p.write_text(json.dumps({'status':'failed','retry_not_before':5000}))
            self.assertTrue(retry_ready(root,audio,now=100))

    def test_new_song_is_not_blocked_by_another_songs_cooldown(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);audio=root/'new.wav';audio.write_bytes(b'new song')
            self.assertTrue(retry_ready(root,audio,now=100))
