#!/usr/bin/env python3
"""Negative controls for the physical unit comparison."""
import copy
from pathlib import Path
import unittest
from CheckUnits import read, validate


class UnitChecks(unittest.TestCase):
    def setUp(self):
        self.reference = read(Path(__file__).with_name('UnitsExpected.txt'))
        self.candidate = copy.deepcopy(self.reference)

    def test_fixture_and_classified_ccd_response(self):
        for scale in ('meter', 'centimeter'):
            self.candidate[scale+'_ccd'][1] = 0.0
        validate(self.reference, self.candidate)

    def test_missing_record(self):
        del self.candidate['meter_rest']
        with self.assertRaises(ValueError): validate(self.reference, self.candidate)

    def test_nonfinite_reference(self):
        self.reference['meter_ray'][0] = float('nan')
        with self.assertRaises(ValueError): validate(self.reference, self.candidate)

    def test_scale_drift_even_inside_engine_tolerance(self):
        self.candidate['centimeter_rest'][0] += 0.001
        with self.assertRaises(ValueError): validate(self.reference, self.candidate)

    def test_wrong_ccd_placement(self):
        for scale in ('meter', 'centimeter'):
            self.candidate[scale+'_ccd'][0] += 0.01
        with self.assertRaises(ValueError): validate(self.reference, self.candidate)

    def test_wrong_sleep_hit_or_cap(self):
        for case, index, value in [('sleep_low', 0, 1), ('high', 1, 0), ('limits', 0, 500)]:
            candidate = copy.deepcopy(self.reference)
            for scale in ('meter', 'centimeter'): candidate[scale+'_'+case][index] = value
            with self.assertRaises(ValueError): validate(self.reference, candidate)


if __name__ == '__main__':
    unittest.main()
