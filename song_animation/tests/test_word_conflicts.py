import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from song_animation.audio_lyrics import strong_word_conflicts,analyze_audio


class WordConflicts(unittest.TestCase):
    def evidence(self):
        return {'words':[{'text':'लिख','start':1,'end':1.3,'probability':.98},
                         {'text':'दिया','start':1.3,'end':1.8,'probability':.98}]}

    def test_confident_wrong_action_is_held(self):
        self.assertTrue(strong_word_conflicts([{'text':'जाम पी लिया','start':0,'end':2}],self.evidence()))

    def test_real_decoder_moderate_verb_and_confident_ending_cannot_be_ignored(self):
        evidence=self.evidence();evidence['words'][0].update(text='दिख',probability=.7532)
        evidence['words'][1]['probability']=.9684
        self.assertTrue(strong_word_conflicts([{'text':'जाम-ए-लब पी लिया','start':0,'end':2}],evidence))

    def test_correct_punctuation_and_weak_or_different_script_are_not_hard_conflicts(self):
        self.assertFalse(strong_word_conflicts([{'text':'जाम लिख दिया।','start':0,'end':2}],self.evidence()))
        self.assertFalse(strong_word_conflicts([{'text':'jaam likh diya','start':0,'end':2}],self.evidence()))
        evidence=self.evidence();evidence['words'][0]['probability']=.7
        self.assertFalse(strong_word_conflicts([{'text':'जाम पी लिया','start':0,'end':2}],evidence))

    def run_audio(self,outputs,td):
        with patch('song_animation.audio_lyrics.duration',return_value=3),patch('song_animation.audio_lyrics.subprocess.run'),patch('pathlib.Path.read_bytes',return_value=b'audio'),patch('song_animation.lyrics.preflight'),patch('song_animation.recognition.independent_audio_text',return_value=self.evidence()),patch('song_animation.audio_lyrics.generate_json',side_effect=outputs) as api:
            result=analyze_audio('unused',td)
            return result,api.call_count

    def data(self,text):
        return {'language':'Hindi','has_vocals':True,'segments':[{'text':text,'start':0,'end':2,'uncertain':False}],'unclear':[],'instrumental':[]}

    def test_positive_reviewer_cannot_override_repeated_lexical_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            # Review is never called: both contradictory transcripts are held first.
            with self.assertRaisesRegex(ValueError,'meaning review'):
                self.run_audio([self.data('जाम पी लिया'),self.data('जाम पी लिया'),{'valid':True}],td)
            self.assertTrue((Path(td)/'audio_hold.json').exists())
            self.assertFalse((Path(td)/'lyrics.json').exists())

    def test_native_correction_requires_audio_review_and_keeps_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            result,calls=self.run_audio([self.data('जाम पी लिया'),self.data('जाम लिख दिया'),{'valid':True}],td)
            self.assertEqual(calls,3)
            self.assertTrue(result['recovery_used'])
            self.assertEqual(result['words'][0]['text'],'जाम लिख दिया')
            self.assertEqual(result['independent_asr'],self.evidence())
