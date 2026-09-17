import unittest
from CheckParallelLifecycle import COMPLETED, inspect_trace


class LifecycleTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = []
        for step in range(44):
            rows += [f"step {step}", "events 0 0 0 0 0", "ccd 1 1"]
            rows += ["body 0"] * (16384 + 7 + (step >= 5))
            rows += [f"lifecycle workers=2 step={step} dispatch={0 if step == 10 else 1} color=1 exact=true"]
        rows += ["callback 1", "sensor_begin 1 2", "sensor_end 1 2", "hit 1 2"]
        rows[3] = "invalid 0"
        rows.append(COMPLETED)
        cls.trace = "\n".join(rows) + "\n"

    def test_complete_trace_and_worker_independence(self):
        digest, dispatches, _ = inspect_trace(self.trace, 2)
        self.assertEqual(dispatches, 43)
        other = self.trace.replace("lifecycle workers=2", "lifecycle workers=4")
        self.assertEqual(digest, inspect_trace(other, 4)[0])

    def test_reject_incomplete_body_trace(self):
        with self.assertRaisesRegex(ValueError, "body trace"):
            inspect_trace(self.trace.replace("body 0\n", "", 1), 2)

    def test_reject_missing_lifecycle_channel(self):
        with self.assertRaisesRegex(ValueError, "channel"):
            inspect_trace(self.trace.replace("callback 1\n", ""), 2)

    def test_reject_configuration_and_dispatch(self):
        for trace in [self.trace.replace("workers=2", "workers=4", 1),
                      self.trace.replace("step=0 dispatch=1", "step=0 dispatch=0"),
                      self.trace.replace("step=10 dispatch=0", "step=10 dispatch=1")]:
            with self.assertRaises(ValueError):
                inspect_trace(trace, 2)

    def test_values_and_order_change_signature(self):
        digest = inspect_trace(self.trace, 2)[0]
        changed = self.trace.replace("callback 1", "callback 2")
        self.assertNotEqual(digest, inspect_trace(changed, 2)[0])
        reordered = self.trace.replace("sensor_begin 1 2\nsensor_end 1 2", "sensor_end 1 2\nsensor_begin 1 2")
        self.assertNotEqual(digest, inspect_trace(reordered, 2)[0])


if __name__ == "__main__":
    unittest.main()
