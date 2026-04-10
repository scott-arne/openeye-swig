"""End-to-end integration tests (@integration tier).

Requires OPENEYE_ROOT and OE_LICENSE environment variables.
Skips gracefully if either is absent.
"""

import subprocess
import sys

import pytest

from conftest import BUILD_DIR, DEFAULT_SLUG


pytestmark = pytest.mark.integration


class TestEndToEnd:

    def test_ctest_passes(self, built_project, openeye_license):
        """C++ GTest suite passes via ctest."""
        result = subprocess.run(
            ["ctest", "--test-dir", BUILD_DIR, "--output-on-failure"],
            cwd=built_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"ctest failed (exit {result.returncode}):\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    def test_pytest_passes(self, built_project, openeye_license):
        """Python pytest suite passes inside the generated project."""
        try:
            import openeye.oechem  # noqa: F401
        except ImportError:
            pytest.skip("openeye-toolkits not importable in current environment")

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/python/", "-v"],
            cwd=built_project,
            capture_output=True,
            text=True,
            env={
                **dict(__import__("os").environ),
                "PYTHONPATH": str(built_project / "python"),
            },
        )
        assert result.returncode == 0, (
            f"pytest failed (exit {result.returncode}):\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
