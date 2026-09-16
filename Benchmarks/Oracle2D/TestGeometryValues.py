import tempfile
from pathlib import Path
import unittest

from CheckGeometryValues import compare, read


class GeometryValueChecks(unittest.TestCase):
    def test_detect_missing_hit_and_initial_overlap_normal(self):
        reference = {'ray_0_1_0': [1, 0, .2, .1, 0, 0]}
        for actual in [[0, 0, .2, .1, 0, 0], [1, 0, .2, .1, 1e-8, 0],
                       [1, 1e-8, .2, .1, 0, 0], [1, 0, .4, .1, 0, 0]]:
            with self.subTest(actual=actual), self.assertRaises(ValueError):
                compare(reference, {'ray_0_1_0': actual})

    def test_detect_nonfinite_output_and_allow_roundoff_after_entry(self):
        reference = {'ray_0_7_3': [1, .5, -1, .2, -1, 0]}
        compare(reference, {'ray_0_7_3': [1, .5, -1, .2, -1, 2e-7]})
        for value in [float('nan'), float('inf'), -float('inf')]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                compare(reference, {'ray_0_7_3': [1, value, -1, .2, -1, 0]})

    def test_reject_empty_truncated_and_duplicate_corpora(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'records.txt'
            for text in ['', 'ray_0_0_0 0 0 0 0 0 0\n', 'ray_0_0_0 0\nray_0_0_0 0\n']:
                with self.subTest(text=text):
                    path.write_text(text)
                    with self.assertRaises(ValueError):
                        read(path)


if __name__ == '__main__':
    unittest.main()
