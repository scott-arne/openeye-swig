#!/usr/bin/env python3
"""Pre-generation hook for cookiecutter template.

Validates user input before generating the project to catch issues early.
"""

import re
import sys


def validate_project_slug(slug):
    """Validate that project_slug is a valid C++ identifier and Python package name."""
    if not re.match(r"^[a-z][a-z0-9_]*$", slug):
        print(
            f"ERROR: project_slug '{slug}' is not a valid identifier.\n"
            f"It must start with a lowercase letter and contain only "
            f"lowercase letters, digits, and underscores.\n"
            f"Tip: choose a project_name using only letters, digits, "
            f"spaces, and hyphens.",
            file=sys.stderr,
        )
        sys.exit(1)


def validate_version(version):
    """Validate that initial_version follows semantic versioning (X.Y.Z)."""
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        print(
            f"ERROR: initial_version '{version}' is not valid.\n"
            f"It must follow semantic versioning: MAJOR.MINOR.PATCH "
            f"(e.g., 0.1.0, 1.0.0).",
            file=sys.stderr,
        )
        sys.exit(1)


validate_project_slug("{{ cookiecutter.project_slug }}")
validate_version("{{ cookiecutter.initial_version }}")
