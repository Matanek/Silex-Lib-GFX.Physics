from pathlib import Path
import tempfile
import unittest
from CheckWorldLifetime import compare, records


class LifetimeChecks(unittest.TestCase):
    def setUp(self):
        self.reference = {f"lifetime_{s}": (int(s != 1),) * 11 for s in range(4)}
        self.actual = {f"lifetime_{s}": (int(s in (0, 3)),) * 11 for s in range(4)}

    def test_complete_lifetime_mapping(self):
        self.assertEqual(compare(self.reference, self.actual), 44)

    def test_every_stage_and_handle(self):
        for side in range(2):
            for stage in range(4):
                for handle in range(11):
                    data = dict(self.reference if side == 0 else self.actual)
                    row = list(data[f"lifetime_{stage}"])
                    row[handle] = 1 - row[handle]
                    data[f"lifetime_{stage}"] = tuple(row)
                    with self.subTest(side=side, stage=stage, handle=handle), self.assertRaises(ValueError):
                        compare(data if side == 0 else self.reference, data if side == 1 else self.actual)

    def test_missing_extra_and_wrong_width(self):
        for data in ({}, self.actual | {"extra": (0,) * 11},
                     self.actual | {"lifetime_1": (0,) * 10}):
            with self.assertRaises(ValueError):
                compare(self.reference, data)

    def test_duplicate_and_non_boolean_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.txt"
            line = "lifetime_0 " + " ".join(["1"] * 11) + "\n"
            for text in (line + line, line.replace(" 1", " nan", 1), line.replace(" 1", " 2", 1)):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    records(path)


if __name__ == "__main__":
    unittest.main()
