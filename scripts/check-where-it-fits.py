#!/usr/bin/env python3
"""Check that a manuscript carries the shared "Where it fits" block word for word.

    check-where-it-fits.py MANUSCRIPT.md [...]

The block is where-it-fits.md beside this script's parent directory: from its
`## Where it fits` heading to its last line. A book may use a deeper heading
level (`###`); the text below the heading must match exactly. Exits 1 on any
mismatch, naming the book and the first differing line.
"""
import pathlib, sys

BLOCK = (pathlib.Path(__file__).resolve().parent.parent / "where-it-fits.md").read_text().strip().splitlines()
BODY = BLOCK[1:]


def check(path):
    lines = pathlib.Path(path).read_text().splitlines()
    starts = [i for i, l in enumerate(lines) if l.lstrip("#").strip() == "Where it fits" and l.startswith("#")]
    if not starts:
        return f"{path}: no 'Where it fits' heading"
    got = lines[starts[0] + 1: starts[0] + 1 + len(BODY)]
    for n, (a, b) in enumerate(zip(BODY, got), 1):
        if a != b:
            return f"{path}: line {n} of the block differs:\n  expected: {a}\n  found:    {b}"
    if len(got) < len(BODY):
        return f"{path}: the block is cut short"
    return None


errors = [e for e in map(check, sys.argv[1:]) if e]
print("\n".join(errors) or f"{len(sys.argv) - 1} manuscripts carry the shared block")
sys.exit(1 if errors else 0)
