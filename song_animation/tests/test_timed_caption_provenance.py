import json,tempfile,unittest
from pathlib import Path
from song_animation.generative import compile_storyboard
from song_animation.tests.test_narrative import narrative
from song_animation.lyrics import cues_from_lyrics,preflight
from song_animation.run import load_analysis_checkpoint
from song_animation.completion import receipt,source_hash

def phrases():
    return {'duration':6,'timing_granularity':'phrase','words':[{'id':i,'text':'एक बात','start':i*2,'end':i*2+1.99} for i in range(3)]}

class TimedStory(unittest.TestCase):
    def test_all_ids_present_still_fails_when_the_scenes_use_wrong_song_times(self):
        plan=narrative()
        for i,s in enumerate(plan['scenes']):s['lyric_ids']=[i]
        compile_storyboard(plan,phrases())
        plan['scenes'][0]['lyric_ids']=[2];plan['scenes'][2]['lyric_ids']=[0]
        with self.assertRaisesRegex(ValueError,'far outside'):compile_storyboard(plan,phrases())

    def test_rounding_at_a_shared_phrase_boundary_does_not_force_a_replan(self):
        plan=narrative()
        for i,s in enumerate(plan['scenes']):s['lyric_ids']=[i]
        plan['scenes'][1]['lyric_ids'].append(0)
        compile_storyboard(plan,phrases())

    def test_long_word_timed_captions_split_only_at_real_word_boundaries(self):
        words=[{'text':'W'*16,'start':i,'end':i+1} for i in range(6)]
        cues=cues_from_lyrics({'words':words},24)
        self.assertEqual([x['start_frame'] for x in cues],[0,48,96])
        self.assertEqual([x['end_frame'] for x in cues],[48,96,144])
        preflight({'words':words})

    def test_long_phrase_without_word_times_is_held_instead_of_inventing_sync(self):
        with self.assertRaisesRegex(ValueError,'too long'):
            preflight({'timing_granularity':'phrase','words':[{'text':' '.join(['W'*16]*6),'start':0,'end':6}]})

    def test_damaged_or_wrong_source_checkpoint_is_not_resumed(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'analysis_checkpoint.json').write_text('{broken')
            self.assertIsNone(load_analysis_checkpoint(p,'key',6))
            (p/'analysis_checkpoint.json').write_text('{"key":"key"}');(p/'lyrics.json').write_text(json.dumps(phrases()))
            self.assertIsNotNone(load_analysis_checkpoint(p,'key',6))
            self.assertIsNone(load_analysis_checkpoint(p,'different-source',6))
            self.assertIsNone(load_analysis_checkpoint(p,'key',3))

class SourceProvenance(unittest.TestCase):
    def test_a_cleared_video_cannot_mark_another_song_or_replaced_excerpt_complete(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);audio=p/'audio.wav';audio.write_bytes(b'source song');video=p/'checked.mp4';video.write_bytes(b'video');clip=p/'source_clip.wav';clip.write_bytes(b'excerpt')
            (p/'status.json').write_text('{"status":"checks_passed"}')
            (p/'selection.json').write_text(json.dumps({'source_sha256':source_hash(audio),'start':12,'duration':2}))
            (p/'quality_gate.json').write_text(json.dumps({'passed':True,'technical':{'video_sha256':source_hash(video),'source_clip_sha256':source_hash(clip)}}))
            self.assertEqual(receipt(audio,p)['clip_start'],12)
            other=p/'another.wav';other.write_bytes(b'another song')
            with self.assertRaisesRegex(ValueError,'different uploaded song'):receipt(other,p)
            clip.write_bytes(b'replaced excerpt')
            with self.assertRaisesRegex(ValueError,'excerpt has changed'):receipt(audio,p)
