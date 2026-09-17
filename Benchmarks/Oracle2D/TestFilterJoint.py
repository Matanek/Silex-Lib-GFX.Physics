from pathlib import Path
import tempfile
import unittest
from CheckFilterJoint import records, compare, TOLERANCES

ROOT = Path(__file__).resolve().parent


class FilterJointChecks(unittest.TestCase):
    def setUp(self):
        self.raw = records(ROOT / "FilterJointRawExpected.txt")
        self.immediate = records(ROOT / "FilterJointImmediateExpected.txt")

    def test_pinned_immediate_mapping(self):
        self.assertEqual(compare(self.raw, self.immediate, self.immediate), 24)

    def test_raw_behavior_cannot_claim_immediate_parity(self):
        with self.assertRaises(ValueError):
            compare(self.raw, self.immediate, self.raw)
        with self.assertRaises(ValueError):
            compare(self.immediate, self.immediate, self.immediate)

    def test_missing_extra_and_duplicate_stages(self):
        missing = dict(self.immediate)
        missing.pop(next(iter(missing)))
        for data in (missing, self.immediate | {"extra": (0,) * 9}):
            with self.assertRaises(ValueError):
                compare(self.raw, self.immediate, data)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.txt"
            text = (ROOT / "FilterJointImmediateExpected.txt").read_text()
            path.write_text(text + text.splitlines()[0] + "\n")
            with self.assertRaises(ValueError):
                records(path)

    def test_each_observable_is_checked(self):
        key = "filter_2_7"
        for column, tolerance in enumerate(TOLERANCES):
            row = list(self.immediate[key])
            row[column] += 1 if tolerance == 0 else 2 * tolerance
            with self.subTest(column=column), self.assertRaises(ValueError):
                compare(self.raw, self.immediate, self.immediate | {key: tuple(row)})

    def test_invalid_numeric_values_and_counts(self):
        key = "filter_0_0"
        for row in ((0,) * 8, (float("nan"),) * 9, (float("inf"),) * 9,
                    (-1,) + (0,) * 8, (0.5,) + (0,) * 8):
            with self.assertRaises(ValueError):
                compare(self.raw, self.immediate, self.immediate | {key: row})

    def test_reference_physical_policy_is_checked(self):
        row = list(self.raw["filter_1_1"])
        row[7] = -2
        with self.assertRaises(ValueError):
            compare(self.raw | {"filter_1_1": tuple(row)}, self.immediate, self.immediate)


if __name__ == "__main__":
    unittest.main()
