import unittest
from song_animation.audio_lyrics import validate_transcript_script
class AudioValidation(unittest.TestCase):
 def test_rejects_original_bad_roman_transcript(self):
  with self.assertRaisesRegex(ValueError,'Roman'):
   validate_transcript_script({'language':'Hindi','segments':[{'text':'ja ja te har ja te koi de de do g mi sa','uncertain':False}]})
 def test_preserves_actual_english(self):
  validate_transcript_script({'language':'English','segments':[{'text':'Walk beside me','uncertain':False}]})
 def test_accepts_original_hindi_and_uncertain_empty_intervals(self):
  validate_transcript_script({'language':'Hindi','segments':[{'text':'मेरे दिल में','uncertain':False},{'text':'','uncertain':True}]})

 def test_semantic_rejection_stops_before_writing_lyrics(self):
  import tempfile
  from pathlib import Path
  from unittest.mock import patch
  from song_animation.audio_lyrics import analyze_audio
  data={'language':'Hindi','has_vocals':True,'segments':[{'text':'मेरे दिल में','uncertain':False,'start':0,'end':2}],'unclear':[]}
  with tempfile.TemporaryDirectory() as td,patch('song_animation.audio_lyrics.duration',return_value=3),patch('song_animation.audio_lyrics.subprocess.run'),patch('pathlib.Path.read_bytes',return_value=b'audio'),patch('song_animation.audio_lyrics.generate_json',side_effect=[data,{'valid':False,'reasons':['Different words in audio']}]) as api:
   with self.assertRaisesRegex(ValueError,'meaning review'):analyze_audio('unused',td)
   self.assertFalse((Path(td)/'lyrics.json').exists())
   self.assertEqual(api.call_count,2)

 def test_code_only_commit_does_not_retranscribe_unrelated_songs(self):
  import tempfile
  from song_animation.select_inputs import select
  with tempfile.TemporaryDirectory() as td:self.assertEqual(select(td),[])
