import unittest
from song_animation.flux_layers import corrected_prompt,prompt_for_asset,environment_prompt

class RepairPrompts(unittest.TestCase):
    def test_review_defects_are_evidence_not_subject_instructions(self):
        context='[{"issues":["Surreal severed hand covering the man\\u0027s eye", "missing people"]}]'
        subject=prompt_for_asset({'id':'kabir_bust','description':'Kabir in a white kurta'}, {})
        result=corrected_prompt(subject,context)
        self.assertNotIn('severed',result)
        self.assertNotIn('missing people',result)
        self.assertIn('connected natural anatomy',result)
        empty=environment_prompt({'bible':{}},{'coverage':{},'visual':'sunlit courtyard'})
        self.assertIn('coherent empty architectural setting',corrected_prompt(empty,context))
        prop=prompt_for_asset({'id':'curtain','description':'teal silk curtain'}, {})
        self.assertIn('Exactly the requested isolated object',corrected_prompt(prop,context))
        self.assertNotIn('character with',corrected_prompt(prop,context))
