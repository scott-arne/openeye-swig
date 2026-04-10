"""Shared fixtures and configuration for cookiecutter template tests."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter

# Path to the cookiecutter template root (one level up from tests/)
TEMPLATE_DIR = str(Path(__file__).resolve().parent.parent)

# Default slug produced by --no-input with cookiecutter.json defaults
DEFAULT_SLUG = "myopeneyeproject"
DEFAULT_PREFIX = "MYOPENEYEPROJECT"
DEFAULT_VERSION = "0.1.0"

# CMake preset used for build/integration tests
CMAKE_PRESET = "ci-debug"
BUILD_DIR = "build-debug"


@pytest.fixture(scope="session")
def generated_project(tmp_path_factory):
    """Generate a project with default settings once per session.

    Returns the Path to the generated project root. Tests using this fixture
    must NOT modify the generated files (use generated_project_custom instead).
    """
    output_dir = tmp_path_factory.mktemp("default")
    project_dir = Path(
        cookiecutter(
            TEMPLATE_DIR,
            no_input=True,
            output_dir=str(output_dir),
        )
    )
    return project_dir


@pytest.fixture
def generated_project_custom(tmp_path):
    """Factory fixture for generating projects with custom template variables.

    Returns a callable: generate(extra_context=None) -> Path
    Each call creates a fresh project in an isolated temp directory.
    """
    def generate(extra_context=None):
        project_dir = Path(
            cookiecutter(
                TEMPLATE_DIR,
                no_input=True,
                output_dir=str(tmp_path),
                extra_context=extra_context or {},
            )
        )
        return project_dir

    return generate


@pytest.fixture(scope="session")
def built_project(generated_project):
    """Configure and build the generated project using CMake presets.

    Writes a CMakeUserPresets.json into the generated project with
    OPENEYE_ROOT and Python3_EXECUTABLE from the current environment.
    Skips all dependent tests if OPENEYE_ROOT is not set.
    """
    openeye_root = os.environ.get("OPENEYE_ROOT")
    if not openeye_root or not os.path.isdir(openeye_root):
        pytest.skip("OPENEYE_ROOT not set or directory does not exist")

    # Write CMakeUserPresets.json with local paths (overrides the
    # placeholder OPENEYE_ROOT in the committed CMakePresets.json)
    user_presets = {
        "version": 6,
        "cmakeMinimumRequired": {"major": 3, "minor": 21, "patch": 0},
        "configurePresets": [
            {
                "name": "ci-debug",
                "inherits": "debug",
                "cacheVariables": {
                    "OPENEYE_ROOT": openeye_root,
                    "Python3_EXECUTABLE": sys.executable,
                },
            }
        ],
        "buildPresets": [
            {"name": "ci-debug", "configurePreset": "ci-debug"}
        ],
    }
    user_presets_path = generated_project / "CMakeUserPresets.json"
    user_presets_path.write_text(json.dumps(user_presets, indent=4))

    result = subprocess.run(
        ["cmake", "--preset", CMAKE_PRESET],
        cwd=generated_project,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail(f"CMake configure failed:\n{result.stderr}")

    result = subprocess.run(
        ["cmake", "--build", "--preset", CMAKE_PRESET],
        cwd=generated_project,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail(f"CMake build failed:\n{result.stderr}")

    return generated_project


@pytest.fixture(scope="session")
def openeye_license():
    """Check that OE_LICENSE is set and the file exists.

    Skips dependent tests if absent.
    """
    oe_license = os.environ.get("OE_LICENSE")
    if not oe_license or not os.path.isfile(oe_license):
        pytest.skip("OE_LICENSE not set or file does not exist")
    return oe_license
