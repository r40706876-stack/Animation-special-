import unittest
from song_animation.flux_layers import prompt_for_asset,body_rig_asset

class BustRigPrompt(unittest.TestCase):
    def test_bust_with_face_in_name_is_not_generated_as_a_detached_portrait(self):
        for name in ('kabir_reaching_bust','meera_bust_intense_profile','meera_profile_face_torso'):
            asset={'id':name,'description':'Expressive profile bust in traditional clothing','subject_kind':'human'}
            self.assertTrue(body_rig_asset(asset))
            prompt=prompt_for_asset(asset,{'characters':'Consistent Indian actors'})
            self.assertIn('head and torso',prompt)
            self.assertIn('hands are hidden behind the body',prompt)
            self.assertNotIn('ONLY the requested portrait head',prompt)
    def test_isolated_hands_stay_isolated(self):
        asset={'id':'kabir_reaching_forearm_hand','description':'One forearm and open hand','subject_kind':'human'}
        self.assertFalse(body_rig_asset(asset))
        self.assertNotIn('head and torso',prompt_for_asset(asset,{}))
