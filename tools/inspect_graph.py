#!/usr/bin/env python3
"""Graph inspection tool for LOF projects."""

import sys

from lof.compilation.compiler import Compiler
from lof.graph.builder import GraphBuilder


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Inspect LOF dependency graph")
    parser.add_argument("--format", choices=["text", "mermaid"], default="text")
    args = parser.parse_args()

    compiler = Compiler()
    compiler.load_all()
    builder = GraphBuilder(compiler.registry)
    builder.build()

    if args.format == "mermaid":
        print(builder.to_mermaid())
        return

    order = builder.get_types_in_order()
    print("Compilation order:")
    for i, t in enumerate(order, 1):
        print(f"  {i}. {t}")

    print("\nDependencies:")
    for t in compiler.registry.types.values():
        if t.depends_on:
            print(f"  {t.id}: depends on {', '.join(t.depends_on)}")
        else:
            print(f"  {t.id}: no dependencies")


if __name__ == "__main__":
    main()
