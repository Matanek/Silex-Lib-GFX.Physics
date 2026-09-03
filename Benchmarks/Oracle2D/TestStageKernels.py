import unittest

from RunStageKernels import PROFILES, compare_states, signature_interval, states, timing


class StageKernelTests(unittest.TestCase):
    profile = PROFILES["integration"]

    def records(self):
        return "\n".join(f"STATE {p} {i} 1 2 3 4 5 0.6 0.8 0" for p in range(8) for i in range(16))

    def test_rejects_missing_duplicate_and_nonfinite_states(self):
        output = self.records()
        for invalid in ("\n".join(output.splitlines()[:-1]), output + "\n" + output.splitlines()[0],
                        output.replace("0.6", "nan", 1), output.replace("0.8 0", "0.8 2", 1)):
            with self.subTest(invalid=invalid[-80:]), self.assertRaises(ValueError):
                states(invalid, self.profile)

    def test_compares_each_component_and_boolean(self):
        reference = states(self.records(), self.profile)
        for index in range(8):
            candidate = reference.copy()
            values = list(candidate[(7, 15)])
            values[index] += 1.0
            candidate[(7, 15)] = values
            with self.subTest(index=index), self.assertRaises(ValueError):
                compare_states(reference, candidate, self.profile)

    def test_local_replay_does_not_use_looser_trajectory_budget(self):
        reference = {(2047, 1): (0.0,) * 8}
        changed = {(2047, 1): (0.001,) + (0.0,) * 7}
        with self.assertRaises(ValueError):
            compare_states(reference, changed, self.profile)

    def test_timing_rejects_wrong_metadata_and_unobserved_output(self):
        final = {(2047, i): (1, 0, 0, 0, 0, 0, 0, 0) for i in range(16)}
        signature = signature_interval(final, self.profile)
        good = "KERNEL integration silex slots8 8192 2048 25 8192"
        timing(good, "integration", "silex", signature)
        for invalid in (good.replace("silex", "clang"), good.replace("slots8", "packed4"),
                        good.replace("2048", "8"), good.replace("25 8192", "25 0"),
                        good.replace("25 8192", "nan 8192")):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                timing(invalid, "integration", "silex", signature)


if __name__ == "__main__":
    unittest.main()
