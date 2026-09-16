from pathlib import Path
import tempfile
import unittest

from CheckZeroStep import compare, records


class ZeroStepChecks(unittest.TestCase):
    def test_reference_matches_and_missing_rows_are_rejected(self):
        reference = records(Path(__file__).with_name('ZeroStepExpected.txt'))
        compare(reference, reference)
        actual = dict(reference)
        del actual['force-positive']
        with self.assertRaisesRegex(ValueError, 'observation sets'):
            compare(reference, actual)

    def test_reject_force_loss_and_premature_contact_event(self):
        reference = records(Path(__file__).with_name('ZeroStepExpected.txt'))
        for key, value in [('force-positive', (0.0, 0.0)),
                           ('contact-zero', (1, 0, 1, 0, 0, 0, 0))]:
            actual = dict(reference)
            actual[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                compare(reference, actual)

    def test_reject_nonfinite_and_duplicate_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'invalid.txt'
            for text in ['force-positive nan 1\n', 'contact-zero inf\n',
                         'force-positive 0 1\nforce-positive 0 1\n']:
                path.write_text(text)
                with self.subTest(text=text), self.assertRaises(ValueError):
                    records(path)


if __name__ == '__main__':
    unittest.main()
