import unittest

from CheckParallelThresholds import inspect_trace


class ThresholdChecks(unittest.TestCase):
    def trace(self, workers=4, dispatch=13, value="0"):
        return "\n".join(
            line for step in range(4)
            for line in [f"step {step}", f"body 0 {value}", "body 1 0", "events 1 2 0 0 0",
                         f"parallel kind=0 count=1 workers={workers} substeps=4 step={step} dispatch={dispatch} color=1 exact=true"]
        ) + "\n"

    def inspect(self, text, workers=4, below=False):
        return inspect_trace(text, 0, 1, workers, 4, below)

    def test_worker_partition_does_not_change_state_signature(self):
        first = self.inspect(self.trace())
        second = self.inspect(self.trace(workers=2, dispatch=9), workers=2)
        self.assertEqual(first[0], second[0])
        self.assertNotEqual(first[1], second[1])

    def test_state_and_event_changes_change_signature(self):
        expected = self.inspect(self.trace())[0]
        self.assertNotEqual(expected, self.inspect(self.trace(value="0.0000001"))[0])
        self.assertNotEqual(expected, self.inspect(self.trace().replace("events 1 2", "events 1 1"))[0])

    def test_incomplete_steps_and_body_traces_are_rejected(self):
        for text in [self.trace().replace("body 1 0\n", "", 1),
                     self.trace().replace("events 1 2 0 0 0\n", "", 1),
                     self.trace().replace("step 2\n", "", 1),
                     self.trace().rsplit("parallel", 1)[0]]:
            with self.assertRaises(ValueError):
                self.inspect(text)

    def test_missing_or_unexpected_dispatch_is_rejected(self):
        with self.assertRaises(ValueError):
            self.inspect(self.trace(dispatch=0))
        with self.assertRaises(ValueError):
            self.inspect(self.trace(), below=True)
        self.inspect(self.trace(dispatch=0), below=True)

    def test_general_contacts_require_both_bodies_and_their_own_kind(self):
        text = self.trace().replace("kind=0", "kind=3")
        inspect_trace(text, 3, 1, 4, 4, False)
        with self.assertRaises(ValueError):
            inspect_trace(text.replace("body 1 0\n", "", 1), 3, 1, 4, 4, False)
        with self.assertRaises(ValueError):
            inspect_trace(text, 0, 1, 4, 4, False)

    def test_wrong_configuration_is_rejected(self):
        for change in ["kind=1", "count=2", "workers=2", "substeps=8"]:
            field = change.split("=")[0]
            original = dict(kind="kind=0", count="count=1", workers="workers=4", substeps="substeps=4")[field]
            with self.assertRaises(ValueError):
                self.inspect(self.trace().replace(original, change))


if __name__ == "__main__":
    unittest.main()
