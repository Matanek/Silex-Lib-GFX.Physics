from pathlib import Path
import tempfile
import unittest
from CheckMotorMouse import REQUIRED, TOLERANCES, compare, records


class MotorMouseChecks(unittest.TestCase):
    def setUp(self):
        self.data = dict.fromkeys(REQUIRED, (0.0,) * 15)

    def test_complete_corpus(self):
        self.assertEqual(compare(self.data, self.data), 1536)

    def test_missing_extra_and_duplicate_keys(self):
        missing = dict(self.data)
        missing.pop(next(iter(missing)))
        for data in (missing, {}, self.data | {"extra": (0.0,) * 15}):
            with self.assertRaises(ValueError):
                compare(self.data, data)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.txt"
            line = "target_0_0_0_1_0 " + " ".join(["0"] * 15) + "\n"
            path.write_text(line + line)
            with self.assertRaises(ValueError):
                records(path)

    def test_all_columns_are_checked(self):
        key = "target_0_1_1_4_2"
        for column, tolerance in enumerate(TOLERANCES):
            row = [0.0] * 15
            row[column] = 1.01 * tolerance
            with self.subTest(column=column), self.assertRaises(ValueError):
                compare(self.data, self.data | {key: tuple(row)})

    def test_roundoff_inside_fixed_thresholds(self):
        row = tuple(t * 0.5 for t in TOLERANCES)
        actual = self.data | {"target_0_1_1_4_2": row}
        self.assertEqual(compare(self.data, actual), 1536)

    def test_nonfinite_and_wrong_width(self):
        for row in ((0,) * 14, (float("nan"),) * 15, (float("inf"),) * 15):
            with self.assertRaises(ValueError):
                compare(self.data, self.data | {"target_0_0_0_1_0": row})

    def test_physical_caps_even_when_both_sides_match(self):
        for key, column, value in [("target_0_0_0_1_0", 12, 1.01),
                                   ("target_0_0_0_1_0", 14, 1.01),
                                   ("target_1_0_7_1_0", 11, 0.01)]:
            row = [0.0] * 15
            row[column] = value
            actual = self.data | {key: tuple(row)}
            with self.assertRaises(ValueError):
                compare(actual, actual)


if __name__ == "__main__":
    unittest.main()
