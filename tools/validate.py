#!/usr/bin/env python3
"""Validation tool for LOF projects."""

import sys

from lof.compilation.compiler import Compiler


def main() -> None:
    compiler = Compiler()
    compiler.load_all()
    errors = compiler.validate_all()
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print("All validations passed")


if __name__ == "__main__":
    main()
