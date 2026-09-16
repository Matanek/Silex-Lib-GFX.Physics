import tempfile
from pathlib import Path
import unittest
from CheckJointConstraints import TOLERANCES, compare, records, required_keys


class JointConstraintChecks(unittest.TestCase):
    def fixture(self, corpus='tuning'):
        return {key: (0.0,) * 9 for key in required_keys(corpus)}

    def test_both_complete_corpora(self):
        for corpus in ('tuning', 'combinations'):
            expected = self.fixture(corpus)
            self.assertEqual(compare(expected, expected, corpus), len(expected))

    def test_reject_missing_case(self):
        expected = self.fixture()
        actual = expected.copy()
        actual.pop(next(iter(actual)))
        with self.assertRaisesRegex(ValueError, 'case sets'):
            compare(expected, actual, 'tuning')

    def test_reject_extra_case(self):
        expected = self.fixture()
        actual = expected | {'unexpected': (0.0,) * 9}
        with self.assertRaisesRegex(ValueError, 'case sets'):
            compare(expected, actual, 'tuning')

    def test_each_numeric_column(self):
        expected = self.fixture()
        key = next(iter(expected))
        for column, tolerance in enumerate(TOLERANCES):
            with self.subTest(column=column):
                actual = expected.copy()
                values = [0.0] * 9
                values[column] = 1.01 * tolerance
                actual[key] = tuple(values)
                with self.assertRaises(ValueError):
                    compare(expected, actual, 'tuning')
                values[column] = 0.5 * tolerance
                actual[key] = tuple(values)
                compare(expected, actual, 'tuning')

    def test_reject_non_finite_or_wrong_width(self):
        expected = self.fixture()
        key = next(iter(expected))
        for values in [(0.0,) * 8, (float('nan'),) * 9, (float('inf'),) * 9]:
            actual = expected | {key: values}
            with self.assertRaises(ValueError):
                compare(expected, actual, 'tuning')

    def test_parser_rejects_duplicate_and_invalid_fields(self):
        line = 'case ' + ' '.join(['0'] * 9) + '\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'records.txt'
            for text in (line + line, 'case 0\n', 'case ' + ' '.join(['nan'] * 9)):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    records(path)


if __name__ == '__main__':
    unittest.main()
