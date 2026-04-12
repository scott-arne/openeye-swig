#!/usr/bin/env python3
"""Post-generation hook for cookiecutter template."""

import subprocess
import sys


def _run(cmd):
    """Run a command, printing a warning on failure instead of aborting."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"WARNING: '{' '.join(cmd)}' failed (exit {result.returncode}).",
            file=sys.stderr,
        )
        if result.stderr.strip():
            print(f"  {result.stderr.strip()}", file=sys.stderr)


# Initialize git repository
_run(["git", "init"])
_run(["git", "add", "."])

print("")
print("Project {{ cookiecutter.project_slug }} created successfully!")
print("")
print("Next steps:")
print("  1. Copy CMakePresets.json to CMakeUserPresets.json and set your OPENEYE_ROOT path")
print("  2. Build: cmake --preset debug && cmake --build build-debug")
print("  3. Install for development: pip install --config-settings editable_mode=compat -e python/")
print("  4. Run tests: pytest tests/python/ -v")
print("")
