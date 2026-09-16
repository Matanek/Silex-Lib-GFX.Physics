import tempfile
from pathlib import Path
import unittest

from CheckDistanceTuning import compare, records


class DistanceTuningChecks(unittest.TestCase):
    def test_reject_missing_transient(self):
        with self.assertRaisesRegex(ValueError, 'case sets'):
            compare({}, {})

    def test_reject_wrong_force_even_with_matching_positions(self):
        reference = {f'distance-{tuning}-{substeps}-{step}': (1.0, 1.0, 0.0, -2.0)
                     for tuning in range(7) for substeps in (1, 2, 4, 8)
                     for step in range(8)}
        actual = dict(reference)
        compare(reference, actual)
        actual['distance-3-4-0'] = (1.0, 1.0, 0.0, -0.5)
        with self.assertRaisesRegex(ValueError, 'field 3'):
            compare(reference, actual)

    def test_reject_duplicate_nonfinite_and_wrong_field_count(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'records.txt'
            for text in ['case 1 1 0 0\ncase 1 1 0 0\n', 'case 1 1 nan 0\n',
                         'case 1 1 0 inf\n', 'case 1 1 0\n']:
                with self.subTest(text=text):
                    path.write_text(text)
                    with self.assertRaises(ValueError):
                        records(path)


if __name__ == '__main__':
    unittest.main()
