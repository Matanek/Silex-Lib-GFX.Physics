#!/usr/bin/env python3
"""Check creation and mutation rejection using precompiled Debug/Release smokes."""
import itertools
from pathlib import Path
import subprocess
import sys

if len(sys.argv) != 3:
    raise SystemExit('usage: check-constraint-tuning.py DEBUG_BINARY RELEASE_BINARY')
for binary in sys.argv[1:]:
    for operation, field, value in itertools.product(
            ['create', 'mutate'], ['hertz', 'damping'], ['negative', 'infinite', 'nan']):
        result = subprocess.run([str(Path(binary).resolve()), operation, field, value],
                                capture_output=True, text=True, timeout=10)
        diagnostic = ('distance joint settings are invalid' if operation == 'create'
                      else 'joint constraint tuning is invalid')
        if result.returncode != 1 or diagnostic not in result.stdout + result.stderr:
            raise SystemExit(f'{binary}: {operation}/{field}/{value}: unexpected result\n'
                             + result.stdout + result.stderr)
print('constraint tuning rejected 24 invalid creation/mutation cases')
