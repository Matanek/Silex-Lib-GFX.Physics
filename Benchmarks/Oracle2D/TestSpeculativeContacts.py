from pathlib import Path
import tempfile
import unittest
from CheckSpeculativeContacts import REQUIRED, TOLERANCES, compare, records


class SpeculativeContactChecks(unittest.TestCase):
    def fixture(self):
        return dict.fromkeys(REQUIRED, (0.0,) * 11)

    def test_complete_corpus(self):
        expected = self.fixture()
        self.assertEqual(compare(expected, expected), 1536)

    def test_missing_extra_or_empty_case_set(self):
        expected = self.fixture()
        missing = expected.copy()
        missing.pop(next(iter(missing)))
        for actual in (missing, {}, expected | {'extra': (0.0,) * 11}):
            with self.assertRaises(ValueError):
                compare(expected, actual)

    def test_every_column_can_fail(self):
        expected = self.fixture()
        key = next(iter(expected))
        for column, tolerance in enumerate(TOLERANCES):
            values = [0.0] * 11
            values[column] = 1 if tolerance == 0 else tolerance * 1.01
            with self.subTest(column=column), self.assertRaises(ValueError):
                compare(expected, expected | {key: tuple(values)})

    def test_fixed_numeric_tolerances_accept_roundoff(self):
        expected = self.fixture()
        actual = {key: tuple(t * 0.5 for t in TOLERANCES) for key in REQUIRED}
        self.assertEqual(compare(expected, actual), 1536)

    def test_non_finite_and_wrong_width(self):
        expected = self.fixture()
        key = next(iter(expected))
        for values in [(0.0,) * 10, (float('nan'),) * 11, (float('inf'),) * 11]:
            with self.assertRaises(ValueError):
                compare(expected, expected | {key: values})

    def test_parser_rejects_duplicates_bad_counts_and_short_lines(self):
        line = 'spec_0_0_0_1_0_0 ' + ' '.join(['0'] * 11) + '\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'corpus.txt'
            for text in (line + line, 'case 0\n', line.replace(' 0 ', ' -1 ', 1),
                         line.replace(' 0 ', ' 0.5 ', 1)):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    records(path)


if __name__ == '__main__':
    unittest.main()
