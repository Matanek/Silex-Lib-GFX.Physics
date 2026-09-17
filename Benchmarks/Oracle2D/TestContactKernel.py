import unittest
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

import RunContactKernel
from RunContactKernel import checked_timing, check_totals, compare_states, parity_result, signature_interval, states, summary, timing


def fixture(full=False):
    return "\n".join(f"STATE {p} {i} " + " ".join(["0"] * 10)
                     for p in range(2048 if full else 8) for i in range(16))


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
                if arguments == ("--check-full",):
                    return fixture(full=True)
                engine = "silex" if binary.name in ("after", "before") else "clang"
                layout = "packed4" if binary.name == "packed" else "slots8"
                elapsed = 80 if binary.name == "before" else 40
                return f"KERNEL {engine} {layout} 2048 2048 {elapsed} 0"

            arguments = ["RunContactKernel.py", "--silex", str(root / "after"),
                         "--baseline-silex", str(root / "before"),
                         "--clang-slots", str(root / "slots"),
                         "--clang-packed", str(root / "packed"),
                         "--box2d-check", str(root / "oracle"),
                         "--output", str(root / "report.json")]
            with patch("sys.argv", arguments), patch.object(RunContactKernel, "execute", execute), \
                 patch.object(RunContactKernel, "replay", return_value=states(fixture(full=True), full=True)), \
                 redirect_stdout(io.StringIO()):
                self.assertEqual(RunContactKernel.main(), 0)
            report = json.loads((root / "report.json").read_text())
            self.assertEqual(report["correctness"]["silex-before"]["short"]["records"], 128)
            self.assertEqual(report["correctness"]["silex-before"]["full"]["records"], 32768)
            self.assertEqual(report["silex_after_over_before"], 0.5)
            self.assertEqual(report["silex_after_over_before_observed_range"], [0.5, 0.5])
            self.assertTrue(all(len(samples) == 7 for samples in report["samples"].values()))
            timed = [name for name, arguments in calls if not arguments]
            self.assertEqual(timed[:4], ["after", "slots", "packed", "before"])
            self.assertEqual(len(timed), 32)
            self.assertEqual(timed[4:12], ["after", "slots", "packed", "before", "slots", "packed", "before", "after"])

    def test_pipeline_rejects_corruption_before_timing(self):
        self.check_pipeline_failure("local", r"field 0", expected_timings=0)

    def test_pipeline_rejects_unstable_signature_inside_allowance(self):
        self.check_pipeline_failure("signature", "unstable final signature", expected_timings=4)

    def check_pipeline_failure(self, failure, message, expected_timings):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("silex", "slots", "packed", "oracle"):
                (root / name).write_bytes(name.encode())
            timed = []

            def execute(binary, *arguments):
                if arguments == ("--check",):
                    return fixture()
                if arguments == ("--check-full",):
                    output = fixture(full=True)
                    if failure == "local" and binary.name == "silex":
                        output = output.replace("STATE 2047 15 0 ", "STATE 2047 15 0.001 ")
                    return output
                timed.append(binary.name)
                engine = "silex" if binary.name == "silex" else "clang"
                layout = "packed4" if binary.name == "packed" else "slots8"
                # Inside the zero fixture's 0.00128 reduction allowance, but
                # different from this executable's already accepted warmup.
                signature = 0.0001 if len(timed) > 3 else 0
                return f"KERNEL {engine} {layout} 2048 2048 40 {signature}"

            arguments = ["RunContactKernel.py", "--silex", str(root / "silex"),
                         "--clang-slots", str(root / "slots"),
                         "--clang-packed", str(root / "packed"),
                         "--box2d-check", str(root / "oracle")]
            with patch("sys.argv", arguments), patch.object(RunContactKernel, "execute", execute), \
                 patch.object(RunContactKernel, "replay", return_value=states(fixture(full=True), full=True)), \
                 redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, message):
                RunContactKernel.main()
            self.assertEqual(len(timed), expected_timings)

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

    def test_long_coverage(self):
        text = fixture(full=True)
        self.assertEqual(len(states(text, full=True)), 32768)
        with self.assertRaises(ValueError):
            states("\n".join(text.splitlines()[:-1]), full=True)

    def test_float32_printing_is_not_trajectory_error(self):
        left = fixture().replace("STATE 0 0 0 ", "STATE 0 0 4096.00048828125 ", 1)
        right = fixture().replace("STATE 0 0 0 ", "STATE 0 0 4096.00049 ", 1)
        self.assertEqual(compare_states(states(left), states(right)), 0)
        with self.assertRaises(ValueError):
            states(fixture().replace("STATE 0 0 0 ", "STATE 0 0 1e100 ", 1))

    def test_total_recurrence_is_exact(self):
        data = states(fixture())
        for key, values in data.items():
            data[key] = (*values[:6], 1.0, 0.0, float(key[0] + 1), 0.0)
        check_totals(data)
        data[7, 0] = (*data[7, 0][:8], 8.000001, 0.0)
        with self.assertRaisesRegex(ValueError, "recurrence"):
            check_totals(data)

    def test_long_velocity_error_is_not_hidden_by_replay(self):
        data = states(fixture(full=True), full=True)
        changed = dict(data)
        changed[2047, 15] = (0.001,) + data[2047, 15][1:]
        with self.assertRaises(ValueError):
            compare_states(data, changed)

    def test_signature_is_bound_to_own_final_states(self):
        data = states(fixture(full=True), full=True)
        for index in range(16):
            data[2047, index] = (1.0,) + data[2047, index][1:]
        interval = signature_interval(data)
        self.assertEqual(interval[0], 2048.0)
        checked_timing("KERNEL silex slots8 2048 2048 40 2048", "silex", interval)
        for output in ["KERNEL silex slots8 2048 2048 40 2049",
                       "KERNEL clang packed4 2048 2048 40 2048"]:
            with self.assertRaises(ValueError):
                checked_timing(output, "silex", interval)

    def test_replay_preserves_keys_and_input_values(self):
        data = states(fixture(full=True), full=True)
        result = type("Result", (), {"returncode": 0, "stdout": fixture(full=True)})()
        with patch.object(RunContactKernel.subprocess, "run", return_value=result) as run:
            self.assertEqual(RunContactKernel.replay(Path("oracle"), data), data)
        command = run.call_args.args[0]
        self.assertEqual(command, ["oracle", "--check-replay"])
        self.assertEqual(states(run.call_args.kwargs["input"], full=True), data)

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
