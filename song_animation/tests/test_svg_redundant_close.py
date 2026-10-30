import unittest
from song_animation.generative import normalize_package
from song_animation.vector import sanitize_svg
class StructuralRecovery(unittest.TestCase):
 def fix(self,s):return normalize_package({'assets':[{'id':'art','svg':s}]})['assets'][0]['svg']
 def test_evidenced_duplicate_defs_close_is_repaired(self):
  s='<svg xmlns="http://www.w3.org/2000/svg"><defs></defs><path d="M0 0L10 10"/></defs></svg>'
  sanitize_svg(self.fix(s));self.assertEqual(self.fix(s).count('</defs>'),1)
 def test_crossed_nesting_is_not_invented(self):
  s='<svg><defs><g></defs></g><path d="M0 0L1 1"/></svg>'
  with self.assertRaises(ValueError):sanitize_svg(self.fix(s))
 def test_safety_validation_still_rejects_scripts_after_structural_repair(self):
  s='<svg><defs></defs><script>bad()</script><path d="M0 0L1 1"/></defs></svg>'
  with self.assertRaisesRegex(ValueError,'Unsupported'):sanitize_svg(self.fix(s))
 def test_leaf_svg_animation_is_removed_from_artwork(self):
  s='<svg xmlns="http://www.w3.org/2000/svg"><circle r="10"><animate attributeName="opacity" values="0;1" dur="1s"/></circle></svg>'
  fixed=self.fix(s);sanitize_svg(fixed);self.assertNotIn('<animate',fixed)
 def test_animation_wrapper_cannot_hide_unsafe_children(self):
  s='<svg><path d="M0 0L1 1"/><animate><script>bad()</script></animate></svg>'
  with self.assertRaises(ValueError):sanitize_svg(self.fix(s))
