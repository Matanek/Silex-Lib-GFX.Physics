import unittest
from CheckMatchedJointWorkers import task_stats


class MatchedWorkerTests(unittest.TestCase):
    def test_complete_small_work(self):
        for workers in [1, 2, 4]:
            row = f"ORACLE_TASKS workers={workers} groups=3 finished=3 items=5 completed=5 mask=1"
            self.assertEqual(task_stats(row, workers)["workers"], str(workers))

    def test_reject_wrong_or_incomplete_work(self):
        good = "ORACLE_TASKS workers=2 groups=3 finished=3 items=5 completed=5 mask=3"
        for old, new in [("workers=2", "workers=4"), ("finished=3", "finished=2"),
                         ("completed=5", "completed=4"), ("mask=3", "mask=4"), ("mask=3", "mask=0")]:
            with self.assertRaises(ValueError):
                task_stats(good.replace(old, new), 2)
        with self.assertRaises(ValueError):
            task_stats(good + "\n" + good, 2)


if __name__ == "__main__":
    unittest.main()
