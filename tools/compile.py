#!/usr/bin/env python3
"""Bazel-friendly compile tool for LOF projects."""

import argparse
import json
import sys
from pathlib import Path

from lof.compilation.compiler import Compiler


def main() -> None:
    parser = argparse.ArgumentParser(description="LOF Compiler")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--types-dir", default="definitions/types")
    parser.add_argument("--instances-dir", default="instances")
    parser.add_argument("--patches-dir", default="patches")
    parser.add_argument("--templates-dir", default="templates")
    parser.add_argument("--targets-dir", default="definitions/targets")
    parser.add_argument("--manifest", action="store_true", help="Generate manifest")
    args = parser.parse_args()

    root = Path.cwd()
    compiler = Compiler(root)
    report = compiler.compile()

    if report.errors:
        for e in report.errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "manifest.json").write_text(
        json.dumps({
            "types": report.types_loaded,
            "instances": report.instances_loaded,
            "patches": report.patches_loaded,
            "generated": report.artifacts_generated,
            "patched": report.artifacts_patched,
        }, indent=2)
    )

    print(f"Generated {len(report.artifacts_generated)} artifacts")


if __name__ == "__main__":
    main()
