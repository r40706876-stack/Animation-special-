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
  with tempfile.TemporaryDirectory() as td,patch('song_animation.audio_lyrics.duration',return_value=3),patch('song_animation.audio_lyrics.subprocess.run'),patch('pathlib.Path.read_bytes',return_value=b'audio'),patch('song_animation.audio_lyrics.generate_json',side_effect=[data,{'valid':False,'reasons':['Different words in audio']},data,{'valid':False,'reasons':['Different words in audio']}]) as api,patch('song_animation.recognition.recovery_evidence',return_value={}):
   with self.assertRaisesRegex(ValueError,'meaning review'):analyze_audio('unused',td)
   self.assertFalse((Path(td)/'lyrics.json').exists())
   self.assertEqual(api.call_count,4)

 def test_code_only_commit_does_not_retranscribe_unrelated_songs(self):
  import tempfile
  from song_animation.select_inputs import select
  with tempfile.TemporaryDirectory() as td:self.assertEqual(select(td),[])

 def test_failed_language_guess_recovers_automatically_with_fingerprint_hint(self):
  import tempfile
  from unittest.mock import patch
  from song_animation.audio_lyrics import analyze_audio
  bad={'language':'Hindi','segments':[{'text':'ja ja te','uncertain':False}]}
  good={'language':'Saraiki','has_vocals':True,'segments':[{'text':'Chalre chalre waal','uncertain':False,'start':0,'end':2}],'unclear':[],'instrumental':[]}
  with tempfile.TemporaryDirectory() as td,patch('song_animation.audio_lyrics.duration',return_value=3),patch('song_animation.audio_lyrics.subprocess.run'),patch('pathlib.Path.read_bytes',return_value=b'audio'),patch('song_animation.recognition.recovery_evidence',return_value={'identity':{'title':'Chalre Chalre Waal'}}) as recovery,patch('song_animation.audio_lyrics.generate_json',side_effect=[bad,good,{'valid':True,'meaning':'curly hair'}]) as api:
   result=analyze_audio('source',td)
   self.assertEqual(result['language'],'Saraiki');self.assertTrue(result['recovery_used']);recovery.assert_called_once()
   self.assertIn('Chalre Chalre Waal',api.call_args_list[1].args[0])
