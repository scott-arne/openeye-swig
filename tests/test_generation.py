"""Tests for cookiecutter template generation (@template tier).

These tests validate that the template renders correctly across all option
combinations. No OpenEye SDK required.
"""

import pytest

from conftest import DEFAULT_SLUG


pytestmark = pytest.mark.template

# All 20 files the template must produce (relative to project root).
EXPECTED_FILES = [
    "CMakeLists.txt",
    "CMakePresets.json",
    "LICENSE",
    "README.md",
    "pyproject.toml",
    "vrzn.toml",
    ".gitignore",
    f"include/{DEFAULT_SLUG}/{DEFAULT_SLUG}.h",
    f"src/{DEFAULT_SLUG}.cpp",
    f"swig/{DEFAULT_SLUG}.i",
    "swig/CMakeLists.txt",
    f"python/{DEFAULT_SLUG}/__init__.py",
    "python/pyproject.toml",
    "scripts/build_python.py",
    "tests/CMakeLists.txt",
    "tests/cpp/CMakeLists.txt",
    f"tests/cpp/test_{DEFAULT_SLUG}.cpp",
    "tests/python/conftest.py",
    f"tests/python/test_{DEFAULT_SLUG}.py",
    ".github/workflows/build-wheels.yml",
]

EXPECTED_DIRS = [
    "include",
    "src",
    "swig",
    "python",
    "tests/cpp",
    "tests/python",
    "scripts",
    ".github/workflows",
]

# Binary extensions to skip when scanning for residual template variables.
BINARY_EXTENSIONS = {".pyc", ".so", ".dylib", ".a", ".o", ".whl", ".egg-info"}


class TestDefaultGeneration:

    def test_default_generation(self, generated_project):
        """cookiecutter --no-input succeeds and output dir has correct name."""
        assert generated_project.exists()
        assert generated_project.name == DEFAULT_SLUG

    def test_expected_files_exist(self, generated_project):
        """All 20 expected files are present."""
        for rel_path in EXPECTED_FILES:
            assert (generated_project / rel_path).is_file(), f"Missing: {rel_path}"

    def test_expected_directories_exist(self, generated_project):
        """Key directories exist."""
        for rel_path in EXPECTED_DIRS:
            assert (generated_project / rel_path).is_dir(), f"Missing dir: {rel_path}"

    def test_no_residual_template_variables(self, generated_project):
        """No {{ cookiecutter. or {% literals remain in generated text files."""
        residuals = []
        for path in generated_project.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix in BINARY_EXTENSIONS:
                continue
            if ".git" in path.parts:
                continue
            if any(part.startswith("build") for part in path.relative_to(generated_project).parts):
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for marker in ("{{ cookiecutter.", "{%"):
                if marker in content:
                    residuals.append(f"{path.relative_to(generated_project)}: {marker}")
        assert residuals == [], f"Residual template variables found:\n" + "\n".join(residuals)

    def test_git_repo_initialized(self, generated_project):
        """Post-gen hook creates .git/ directory."""
        assert (generated_project / ".git").is_dir()

    def test_gitignore_references_project_slug(self, generated_project):
        """The .gitignore references SWIG-generated files with the correct slug."""
        content = (generated_project / ".gitignore").read_text()
        assert f"python/{DEFAULT_SLUG}/{DEFAULT_SLUG}.py" in content
        assert f"python/{DEFAULT_SLUG}/_{DEFAULT_SLUG}.so" in content


class TestOptionVariants:

    @pytest.mark.parametrize("license_choice,expected_text", [
        ("MIT", "MIT License"),
        ("BSD-3-Clause", "BSD 3-Clause License"),
        ("Apache-2.0", "Apache License, Version 2.0"),
    ])
    def test_license_variants(self, generated_project_custom, license_choice, expected_text):
        """Each license choice generates the correct license text."""
        project = generated_project_custom(extra_context={"license": license_choice})
        content = (project / "LICENSE").read_text()
        assert expected_text in content

    @pytest.mark.parametrize("use_stable_abi,should_contain", [
        ("true", True),
        ("false", False),
    ])
    def test_stable_abi_variants(self, generated_project_custom, use_stable_abi, should_contain):
        """Stable ABI option controls pyproject.toml scikit-build settings."""
        project = generated_project_custom(
            extra_context={"use_stable_abi": use_stable_abi}
        )
        pyproject = (project / "pyproject.toml").read_text()
        if should_contain:
            assert "wheel.py-api" in pyproject
            assert 'MYOPENEYEPROJECT_USE_STABLE_ABI = "ON"' in pyproject
        else:
            assert "wheel.py-api" not in pyproject
            assert 'MYOPENEYEPROJECT_USE_STABLE_ABI = "ON"' not in pyproject

    def test_custom_project_name(self, generated_project_custom):
        """Custom name produces correct slug and prefix in paths and content."""
        project = generated_project_custom(
            extra_context={"project_name": "Mol Analyzer"}
        )
        slug = "molanalyzer"
        prefix = "MOLANALYZER"

        assert project.name == slug
        assert (project / f"include/{slug}/{slug}.h").is_file()
        assert (project / f"src/{slug}.cpp").is_file()
        assert (project / f"swig/{slug}.i").is_file()

        header = (project / f"include/{slug}/{slug}.h").read_text()
        assert f"namespace {prefix}" in header
        assert f"{prefix}_H" in header

        cmake = (project / "CMakeLists.txt").read_text()
        assert f"project({slug}" in cmake
