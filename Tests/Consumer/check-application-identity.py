#!/usr/bin/env python3
"""Check stale identity reads/writes and mutations during contact callbacks."""
from pathlib import Path
import subprocess
import sys

if len(sys.argv) != 3:
    raise SystemExit('usage: check-application-identity.py DEBUG_BINARY RELEASE_BINARY')
for binary in sys.argv[1:]:
    for family, diagnostic in [('body', 'no longer refers to a live body'),
                               ('collider', 'no longer refers to a live collider'),
                               ('joint', 'no longer refers to a live joint')]:
        for operation in ['read', 'write', 'locked']:
            expected = 'cannot be modified during step or refresh_contacts' if operation == 'locked' else diagnostic
            result = subprocess.run([str(Path(binary).resolve()), family, operation],
                                    capture_output=True, text=True, timeout=10)
            if result.returncode != 1 or expected not in result.stdout + result.stderr:
                raise SystemExit(f'{family}/{operation}: unexpected exit {result.returncode}\n'
                                 + result.stdout + result.stderr)
print('application identity rejected 18 invalid reads and mutations')
