import unittest
from CheckParallelJointFamilies import inspect_trace


class JointFamilyTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = []
        for step in range(8):
            rows.append(f"step {step}")
            rows += ["body 0"] * 8192
            rows += [f"joint {i % 7} {i} 1 2 3 4 5" for i in range(4096)]
            rows.append(f"families workers=2 substeps=4 step={step} dispatch=13 color=4096 exact=true")
        cls.trace = "\n".join(rows) + "\n"

    def test_complete_trace_and_worker_independence(self):
        digest, dispatches, _ = inspect_trace(self.trace, 2, 4)
        self.assertEqual(dispatches, 104)
        other = self.trace.replace("families workers=2", "families workers=4")
        self.assertEqual(digest, inspect_trace(other, 4, 4)[0])

    def test_reject_incomplete_trace(self):
        for row in ["body 0\n", "joint 0 0 1 2 3 4 5\n", "step 0\n"]:
            with self.assertRaises(ValueError):
                inspect_trace(self.trace.replace(row, "", 1), 2, 4)

    def test_reject_wrong_family_or_order(self):
        for changed in ["joint 1 0 1 2 3 4 5", "joint 0 7 1 2 3 4 5"]:
            with self.assertRaisesRegex(ValueError, "family or identity"):
                inspect_trace(self.trace.replace("joint 0 0 1 2 3 4 5", changed, 1), 2, 4)

    def test_reject_configuration_and_dispatch(self):
        for old, new in [("workers=2", "workers=4"), ("substeps=4", "substeps=2"),
                         ("dispatch=13", "dispatch=0"), ("color=4096", "color=4095")]:
            with self.assertRaises(ValueError):
                inspect_trace(self.trace.replace(old, new, 1), 2, 4)

    def test_values_change_signature(self):
        changed = self.trace.replace("joint 0 0 1 2 3 4 5", "joint 0 0 1 2 3 4 6", 1)
        self.assertNotEqual(inspect_trace(self.trace, 2, 4)[0], inspect_trace(changed, 2, 4)[0])


if __name__ == "__main__":
    unittest.main()
