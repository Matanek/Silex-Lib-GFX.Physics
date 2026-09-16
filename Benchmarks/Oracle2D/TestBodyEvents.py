import tempfile
import unittest
from pathlib import Path
from CheckBodyEvents import compare, records


class BodyEventsChecks(unittest.TestCase):
    def setUp(self):
        self.rows = {f'stage_{i}': (0,) * 9 for i in range(10)}
        self.rows['stage_0'] = (1, 1, 0, 0, 0, 0, 1, 0, 1)

    def read(self, text):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'events.txt'
            path.write_text(text)
            return records(path)

    def serialize(self):
        return '\n'.join(key + ' ' + ' '.join(map(str, value)) for key, value in self.rows.items())

    def test_complete_match(self):
        compare(self.rows, self.read(self.serialize()))

    def test_missing_stage(self):
        with self.assertRaises(ValueError):
            self.read('\n'.join(self.serialize().splitlines()[:-1]))

    def test_duplicate_stage(self):
        with self.assertRaises(ValueError):
            self.read(self.serialize() + '\n' + self.serialize().splitlines()[0])

    def test_swapped_surface(self):
        actual = dict(self.rows)
        actual['stage_0'] = (1, 2, 0, 0, 0, 0, 1, 0, 1)
        with self.assertRaises(ValueError):
            compare(self.rows, actual)

    def test_manufactured_transition(self):
        actual = dict(self.rows)
        actual['stage_1'] = (1, 2, 0, 0, 0, 0, 0, 0, 0)
        with self.assertRaises(ValueError):
            compare(self.rows, actual)

    def test_wrong_record_width(self):
        with self.assertRaises(ValueError):
            self.read(self.serialize() + ' 0')

    def test_noninteger_payload(self):
        with self.assertRaises(ValueError):
            self.read(self.serialize().replace('stage_0 1', 'stage_0 nan'))

    def test_extra_stage(self):
        actual = dict(self.rows, stage_10=(0,) * 9)
        with self.assertRaises(ValueError):
            compare(self.rows, actual)


if __name__ == '__main__':
    unittest.main()
