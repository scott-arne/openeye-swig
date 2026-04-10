"""Tests for CMake configure and build (@build tier).

Requires OPENEYE_ROOT environment variable pointing to the OpenEye C++ SDK.
Skips gracefully if absent.
"""

import sys

import pytest

from conftest import BUILD_DIR, DEFAULT_SLUG


pytestmark = pytest.mark.build


class TestCMakeBuild:

    def test_cmake_configure(self, built_project):
        """CMake configure succeeded (validated by built_project fixture)."""
        assert (built_project / BUILD_DIR / "CMakeCache.txt").is_file()

    def test_cmake_build(self, built_project):
        """CMake build succeeded -- static library exists."""
        lib_dir = built_project / BUILD_DIR
        # Look for the static library (libmyopeneyeproject.a on Unix)
        libs = list(lib_dir.rglob(f"lib{DEFAULT_SLUG}.a"))
        if not libs:
            libs = list(lib_dir.rglob(f"{DEFAULT_SLUG}.lib"))
        assert libs, f"Static library for {DEFAULT_SLUG} not found in {BUILD_DIR}/"

    def test_swig_module_exists(self, built_project):
        """SWIG extension module produced in python/<slug>/."""
        python_dir = built_project / "python" / DEFAULT_SLUG
        ext = ".so" if sys.platform != "win32" else ".pyd"
        modules = list(python_dir.glob(f"_{DEFAULT_SLUG}*{ext}"))
        assert modules, f"SWIG module _{DEFAULT_SLUG}*{ext} not found in {python_dir}"

    def test_gtest_binary_exists(self, built_project):
        """GTest binary produced in the build directory."""
        build_dir = built_project / BUILD_DIR
        binaries = list(build_dir.rglob(f"{DEFAULT_SLUG}_tests"))
        if not binaries:
            binaries = list(build_dir.rglob(f"{DEFAULT_SLUG}_tests.exe"))
        assert binaries, f"GTest binary {DEFAULT_SLUG}_tests not found in {BUILD_DIR}/"
