import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from song_animation.generative import build,PROTOCOL

class BackendCache(unittest.TestCase):
    def test_art_backend_change_keeps_exact_source_story(self):
        lyrics={'duration':5,'words':[]};music={}
        key=hashlib.sha256((PROTOCOL+'painted-layers'+json.dumps([lyrics,music],sort_keys=True,ensure_ascii=False)).encode()).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            Path(td,'vector_checkpoint.json').write_text(json.dumps({'key':key}))
            Path(td,'storyboard.json').write_text(json.dumps({'scenes':[],'title':'Same source story'}))
            with patch('song_animation.generative.storyboard') as generate:
                plan=build(lyrics,music,td,artwork='flux-layers',plan_only=True)
                self.assertEqual(plan['title'],'Same source story');generate.assert_not_called()

    def test_different_audio_analysis_cannot_reuse_the_story(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td,'vector_checkpoint.json').write_text(json.dumps({'key':'wrong-source-key'}))
            Path(td,'storyboard.json').write_text(json.dumps({'scenes':[],'title':'Wrong source'}))
            with patch('song_animation.generative.storyboard',return_value={'scenes':[],'title':'Correct new story'}) as generate:
                plan=build({'duration':5,'words':[]},{},td,artwork='flux-layers',plan_only=True)
                self.assertEqual(plan['title'],'Correct new story');generate.assert_called_once()
