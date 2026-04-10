#!/usr/bin/env python3
"""Post-generation hook for cookiecutter template."""

import subprocess

# Initialize git repository
subprocess.run(["git", "init"], check=False)
subprocess.run(["git", "add", "."], check=False)

print("")
print("Project {{ cookiecutter.project_slug }} created successfully!")
print("")
print("Next steps:")
print("  1. Copy CMakePresets.json to CMakeUserPresets.json and set your OPENEYE_ROOT path")
print("  2. Build: cmake --preset debug && cmake --build build-debug")
print("  3. Install for development: pip install --config-settings editable_mode=compat -e python/")
print("  4. Run tests: pytest tests/python/ -v")
print("")
