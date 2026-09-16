#!/usr/bin/env python3
"""Ensure malformed or physically invalid contact-pair evidence is rejected."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent


class ContactPairChecks(unittest.TestCase):
    def check(self, kind, mutation=None, accepted=False, reference_mutation=None):
        original = (ROOT / (kind + 'Expected.txt')).read_text()
        with tempfile.TemporaryDirectory() as directory:
            reference = pathlib.Path(directory) / 'reference.txt'
            candidate = pathlib.Path(directory) / 'candidate.txt'
            reference.write_text(reference_mutation(original) if reference_mutation else original)
            candidate.write_text(mutation(original) if mutation else original)
            result = subprocess.run([sys.executable, '-B', str(ROOT / ('Check' + kind + '.py')),
                                     str(reference), str(candidate)], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, accepted, result.stdout + result.stderr)

    def test_pinned_fixtures(self):
        for kind in ('Geometry', 'DynamicShapes'):
            self.check(kind, accepted=True)

    def test_missing_pair(self):
        for kind in ('Geometry', 'DynamicShapes'):
            self.check(kind, lambda text: '\n'.join(line for line in text.splitlines()
                                                   if 'segment_circle' not in line))

    def test_duplicate_pair(self):
        for kind in ('Geometry', 'DynamicShapes'):
            self.check(kind, lambda text: text + next(line for line in text.splitlines()
                                                     if 'capsule_capsule' in line) + '\n')

    def test_bad_manifold_count(self):
        self.check('Geometry', lambda text: text.replace('segment_circle 1 ', 'segment_circle 2 '))

    def test_wrong_normal(self):
        self.check('Geometry', lambda text: text.replace('segment_circle 1 0 1 ', 'segment_circle 1 0 -1 '))

    def test_nonfinite_both_sides(self):
        for kind in ('Geometry', 'DynamicShapes'):
            def mutate(text):
                lines = text.splitlines()
                fields = lines[0].split()
                fields[-1] = 'nan'
                lines[0] = ' '.join(fields)
                return '\n'.join(lines)
            self.check(kind, mutate, reference_mutation=mutate)

    def test_transient_velocity_error(self):
        self.check('DynamicShapes', lambda text: text.replace('-4.99999905', '-4.8', 1))

    def test_final_spin_even_inside_differential_tolerance(self):
        def mutate(text):
            lines = text.splitlines()
            for index, line in enumerate(lines):
                if line.startswith('pair_segment_circle_240 '):
                    fields = line.split()
                    fields[-1] = '0.06'
                    lines[index] = ' '.join(fields)
            return '\n'.join(lines)
        self.check('DynamicShapes', mutate)


if __name__ == '__main__':
    unittest.main()
