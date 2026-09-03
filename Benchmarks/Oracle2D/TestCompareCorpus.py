import unittest

from CheckCorpus import summarize
from CompareCorpus import WORKLOAD, compare


def records():
    result = []
    for engine, time in (("box2d-3.1.1", "2"), ("silex-current", "1")):
        for _ in range(7):
            result.append(dict(
                schema="2", engine=engine, workload=WORKLOAD,
                scenario="circle-5000", mode="release", workers="1",
                bodies="5000", steps="300", dt="0.016666668", substeps="4",
                gravity_y="-10", contact_hertz="30", contact_damping="10",
                body_mass="1", sleep_enabled="false", step_ms=time,
                elapsed_ms=str(float(time) * 300), centroid_x="0", centroid_y="-2.4",
                max_speed="0", min_y="-2.977", max_overlap_mm="16",
                contacts="10000", awake="5000", state_signature=engine,
            ))
    return result


class CompareCorpusTests(unittest.TestCase):
    def test_equivalent_faster_workload(self):
        reports, failures = compare(records())
        self.assertFalse(failures)
        self.assertIn("Silex/Box2D=0.500000", reports[-1])

    def test_absolute_cadence_does_not_prove_parity(self):
        rows = records()
        for row in rows[7:]:
            row["step_ms"] = "3"
        self.assertTrue(any("exceeds parity" in failure for failure in compare(rows)[1]))

    def test_historical_metadata_rejected(self):
        rows = records()
        for row in rows:
            row.pop("workload")
        self.assertTrue(compare(rows)[1])

    def test_all_configuration_mismatches_rejected(self):
        for key, value in (("substeps", "2"), ("gravity_y", "-9.81"),
                           ("contact_hertz", "40"), ("body_mass", "0.01"),
                           ("workers", "4"), ("steps", "600"),
                           ("bodies", "1800"), ("dt", "0.01"),
                           ("contact_damping", "5"), ("sleep_enabled", "true")):
            with self.subTest(key=key):
                rows = records()
                rows[-1][key] = value
                self.assertTrue(any(f"mismatched {key}" in failure
                                    for failure in compare(rows)[1]))

    def test_missing_engine_and_small_series_rejected(self):
        self.assertTrue(compare(records()[:7])[1])
        self.assertTrue(compare(records()[:-1])[1])

    def test_correctness_and_determinism_rejected_before_success(self):
        for key, value in (("max_overlap_mm", "21"), ("awake", "4999"),
                           ("state_signature", "changed"), ("step_ms", "0"),
                           ("mode", "debug"), ("gravity_y", "nan")):
            with self.subTest(key=key):
                rows = records()
                rows[-1][key] = value
                self.assertTrue(compare(rows)[1])

    def test_no_implicit_noise_allowance(self):
        rows = records()
        for row in rows[7:]:
            row["step_ms"] = "2"
        rows[-1]["step_ms"] = "2.01"
        self.assertTrue(any("inconclusive" in failure for failure in compare(rows)[1]))

    def test_workloads_are_not_pooled(self):
        rows = records()[7:]
        older = [dict(row, workload="legacy-silex", state_signature="older")
                 for row in rows]
        _, failures = summarize(rows + older)
        self.assertFalse(failures)


if __name__ == "__main__":
    unittest.main()
