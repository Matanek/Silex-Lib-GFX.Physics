#!/usr/bin/env python3
"""Check every retained handle family after world finalization from the workspace root."""
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
    source = Path(__file__).resolve().parent / "Smokes/InvalidWorldLifetime.sx"
    expected = {
        "body": "GFX.Physics.RigidBody2D no longer refers to a live body",
        "collider": "GFX.Physics.Collider2D no longer refers to a live collider",
        "chain": "GFX.Physics.Collider2D no longer refers to a live collider",
    }
    for kind in ["distance", "filter", "motor", "mouse", "prismatic", "revolute", "weld", "wheel"]:
        expected[kind] = "GFX.Physics joint handle no longer refers to a live joint"
    with tempfile.TemporaryDirectory(prefix="physics-world-lifetime-") as temporary:
        binary = Path(temporary).resolve() / "InvalidWorldLifetime"
        subprocess.run([args.compiler, "compile", str(source), "--backend", args.backend,
                        "--" + args.mode, "-o", str(binary)], check=True)
        for kind, diagnostic in expected.items():
            result = subprocess.run([str(binary), kind], capture_output=True, text=True, timeout=30)
            if result.returncode != 1 or diagnostic not in result.stdout + result.stderr:
                raise AssertionError((kind, result.returncode, result.stdout, result.stderr))
            print(kind + ": rejected with the expected diagnostic")
    print("11 finalized-world handle accesses rejected")


if __name__ == "__main__":
    main()
