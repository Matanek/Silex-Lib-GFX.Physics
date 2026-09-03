import unittest
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

import RunContactKernel
from RunContactKernel import compare_states, parity_result, states, summary, timing


def fixture():
    return "\n".join(f"STATE {p} {i} " + " ".join(["0"] * 10) for p in range(8) for i in range(16))


class ContactKernelChecks(unittest.TestCase):
    def test_baseline_joins_correctness_warmup_and_alternating_series(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("after", "before", "slots", "packed", "oracle"):
                (root / name).write_bytes(name.encode())
            calls = []

            def execute(binary, *arguments):
                calls.append((binary.name, arguments))
                if arguments == ("--check",):
                    return fixture()
                engine = "silex" if binary.name in ("after", "before") else "clang"
                layout = "packed4" if binary.name == "packed" else "slots8"
                elapsed = 80 if binary.name == "before" else 40
                return f"KERNEL {engine} {layout} 2048 2048 {elapsed} 123"

            arguments = ["RunContactKernel.py", "--silex", str(root / "after"),
                         "--baseline-silex", str(root / "before"),
                         "--clang-slots", str(root / "slots"),
                         "--clang-packed", str(root / "packed"),
                         "--box2d-check", str(root / "oracle"),
                         "--output", str(root / "report.json")]
            with patch("sys.argv", arguments), patch.object(RunContactKernel, "execute", execute), redirect_stdout(io.StringIO()):
                self.assertEqual(RunContactKernel.main(), 0)
            report = json.loads((root / "report.json").read_text())
            self.assertEqual(report["correctness"]["silex-before"]["records"], 128)
            self.assertEqual(report["silex_after_over_before"], 0.5)
            self.assertEqual(report["silex_after_over_before_observed_range"], [0.5, 0.5])
            self.assertTrue(all(len(samples) == 7 for samples in report["samples"].values()))
            timed = [name for name, arguments in calls if not arguments]
            self.assertEqual(timed[:4], ["after", "slots", "packed", "before"])
            self.assertEqual(len(timed), 32)
            self.assertEqual(timed[4:12], ["after", "slots", "packed", "before", "slots", "packed", "before", "after"])

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
