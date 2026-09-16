import math
from pathlib import Path
import tempfile
import unittest
from CheckCompoundContacts import compare, records


class CompoundContactChecks(unittest.TestCase):
    def setUp(self):
        self.rows = {f'stage_{i}': (2, 3, 0, 0, 0, 0, 2, 3) for i in range(24)}
        self.rows.update({f'precontact_{i}': (0, 0) for i in range(4)})
        self.rows['support'] = (2, 3, 0, 1, 0, 0, 0)

    def read(self, rows):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'contacts.txt'
            path.write_text('\n'.join(k+' '+' '.join(map(str,v)) for k,v in rows.items()))
            return records(path)

    def test_complete_match(self):
        compare(self.rows, self.read(self.rows))

    def test_missing_stage(self):
        del self.rows['stage_19']
        with self.assertRaises(ValueError):
            self.read(self.rows)

    def test_lost_surface(self):
        actual = dict(self.rows)
        actual['stage_0'] = (1, 1, 0, 0, 0, 0, 1, 1)
        with self.assertRaises(ValueError):
            compare(self.rows, actual)

    def test_wrong_end_identity(self):
        actual = dict(self.rows)
        actual['stage_5'] = (2, 3, 1, 2, 0, 0, 2, 3)
        with self.assertRaises(ValueError):
            compare(self.rows, actual)

    def test_manufactured_precontact_begin(self):
        actual = dict(self.rows, precontact_1=(1, 0))
        with self.assertRaises(ValueError):
            compare(self.rows, actual)

    def test_nonfinite_support(self):
        self.rows['support'] = (2, 3, 0, math.nan, 0, 0, 0)
        with self.assertRaises(ValueError):
            self.read(self.rows)

    def test_body_falls_through_supports(self):
        actual = dict(self.rows, support=(2, 3, 0, 0.9, 0, 0, 0))
        with self.assertRaises(ValueError):
            compare(self.rows, actual)

    def test_missing_physical_support(self):
        actual = dict(self.rows, support=(1, 1, 0, 1, 0, 0, 0))
        with self.assertRaises(ValueError):
            compare(self.rows, actual)


if __name__ == '__main__':
    unittest.main()
