#!/usr/bin/env python3
"""Check joint observations after world finalization from the workspace root."""
import argparse
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", default="silex")
    parser.add_argument("--backend", default="llvm", choices=["llvm", "native"])
    parser.add_argument("--mode", choices=["debug", "release"], required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent / "Smokes/InvalidJointObservations.sx"
    cases = [(kind, field) for kind in ["distance", "filter", "motor", "mouse", "prismatic", "revolute", "weld", "wheel"]
             for field in ["linear", "angular"]]
    cases += [("distance", "measure"), ("prismatic", "measure"), ("prismatic", "speed"),
              ("revolute", "measure"), ("wheel", "measure"), ("wheel", "speed")]
    diagnostic = "GFX.Physics joint handle no longer refers to a live joint"
    with tempfile.TemporaryDirectory(prefix="physics-world-lifetime-") as temporary:
        binary = Path(temporary).resolve() / "InvalidJointObservations"
        subprocess.run([args.compiler, "compile", str(source), "--backend", args.backend,
                        "--" + args.mode, "-o", str(binary)], check=True)
        for kind, field in cases:
            result = subprocess.run([str(binary), kind, field], capture_output=True, text=True, timeout=30)
            if result.returncode != 1 or diagnostic not in result.stdout + result.stderr:
                raise AssertionError((kind, field, result.returncode, result.stdout, result.stderr))
            print(kind + "/" + field + ": rejected with the expected diagnostic")
    print("22 stale joint observations rejected")


if __name__ == "__main__":
    main()
