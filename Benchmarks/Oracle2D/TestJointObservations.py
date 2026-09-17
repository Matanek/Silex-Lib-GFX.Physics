import math
from pathlib import Path
import tempfile
import unittest
from CheckJointObservations import KEYS, TOLERANCES, compare, records


class JointObservationsChecks(unittest.TestCase):
    def setUp(self):
        self.data = {key: (0.0,) * 6 for key in KEYS}

    def test_complete(self):
        self.assertEqual(compare(self.data, self.data), 512)

    def test_each_field_has_a_fixed_bound(self):
        for column, tolerance in enumerate(TOLERANCES):
            row = [0.0] * 6
            row[column] = 2 * tolerance
            with self.subTest(column=column), self.assertRaises(ValueError):
                compare(self.data, self.data | {"observe_0_0_0_0": tuple(row)})

    def test_missing_extra_width_and_nonfinite(self):
        bad = [{}, self.data | {"extra": (0.0,) * 6},
               self.data | {"observe_0_0_0_0": (0.0,) * 5}]
        for value in (math.nan, math.inf, -math.inf):
            for column in range(6):
                row = [0.0] * 6; row[column] = value
                bad.append(self.data | {"observe_0_0_0_0": tuple(row)})
        for data in bad:
            with self.assertRaises(ValueError): compare(self.data, data)
            with self.assertRaises(ValueError): compare(data, self.data)

    def test_duplicate_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.txt"
            path.write_text("observe_0_0_0_0 0 0 0 0 0 0\n" * 2)
            with self.assertRaises(ValueError): records(path)
