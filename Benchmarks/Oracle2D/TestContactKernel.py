import unittest

from RunContactKernel import compare_states, parity_result, states, summary, timing


def fixture():
    return "\n".join(f"STATE {p} {i} " + " ".join(["0"] * 10) for p in range(8) for i in range(16))


class ContactKernelChecks(unittest.TestCase):
    def test_complete_fixture(self):
        records = states(fixture())
        self.assertEqual(len(records), 128)
        self.assertEqual(compare_states(records, records), 0)

    def test_missing_record(self):
        with self.assertRaises(ValueError):
            states("\n".join(fixture().splitlines()[:-1]))

    def test_duplicate_record(self):
        with self.assertRaises(ValueError):
            states(fixture() + "\n" + fixture().splitlines()[0])

    def test_nonfinite_state(self):
        with self.assertRaises(ValueError):
            states(fixture().replace(" 0 0 0 0 0 0 0 0 0 0", " nan 0 0 0 0 0 0 0 0 0", 1))

    def test_changed_velocity(self):
        reference = states(fixture())
        changed = dict(reference)
        changed[0, 0] = (0.001,) + reference[0, 0][1:]
        with self.assertRaises(ValueError):
            compare_states(reference, changed)

    def test_wrong_fields(self):
        with self.assertRaises(ValueError):
            states(fixture().replace("STATE 0 0 ", "STATE 0 0 1 ", 1))

    def test_timing(self):
        self.assertEqual(timing("KERNEL silex slots8 2048 2048 40 123")["elapsed_ms"], 40)

    def test_wrong_timing_contract(self):
        for value in ("KERNEL silex slots8 2048 1024 40 123",
                      "KERNEL silex slots8 2048 2048 nan 123",
                      "KERNEL silex slots8 2048 2048 40 inf",
                      "KERNEL silex slots8 2048 2048 0 123",
                      "KERNEL unknown slots8 2048 2048 40 123"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                timing(value)

    def test_median_and_mad(self):
        result = summary([{"elapsed_ms": v} for v in [10, 9, 11, 12, 8, 10, 10]])
        self.assertEqual(result["median_ms"], 10)
        self.assertEqual(result["mad_percent"], 10)

    def test_parity_gate(self):
        reference = {"min_ms": 40, "max_ms": 42}
        for candidate, admissible, expected in [
            ({"min_ms": 30, "max_ms": 39}, True, "demonstrated-for-this-kernel"),
            ({"min_ms": 43, "max_ms": 50}, True, "missed"),
            ({"min_ms": 39, "max_ms": 41}, True, "inconclusive"),
            ({"min_ms": 30, "max_ms": 39}, False, "inadmissible"),
        ]:
            with self.subTest(expected=expected):
                self.assertEqual(parity_result(candidate, reference, admissible), expected)


if __name__ == "__main__":
    unittest.main()
