#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

for binary in sys.argv[1:]:
    for option in ['contact', 'hit']:
        for lifetime in ['stale', 'locked']:
            result = subprocess.run([str(Path(binary).resolve()), option, lifetime], capture_output=True, text=True, timeout=10)
            diagnostic = 'no longer refers to a live body' if lifetime == 'stale' else 'cannot be modified during step or refresh_contacts'
            if result.returncode != 1 or diagnostic not in result.stdout + result.stderr:
                raise SystemExit(f'{option}/{lifetime}: unexpected result {result.returncode}\n'+result.stdout+result.stderr)
print('body events rejected 8 stale/locked mutations')
