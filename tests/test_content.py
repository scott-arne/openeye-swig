"""Tests for generated file content validation (@template tier).

These tests validate the semantic correctness of generated files: valid syntax,
correct variable substitutions, version consistency, etc.
"""

import ast
import json
import sys

import pytest
import yaml

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

from vrzn.config import find_config, load_config, validate_config
from vrzn.locations import locations_from_config, check_agreement

from conftest import DEFAULT_SLUG, DEFAULT_PREFIX, DEFAULT_VERSION


pytestmark = pytest.mark.template


class TestPythonSyntax:

    def test_python_files_parse(self, generated_project):
        """All .py files are syntactically valid Python."""
        failures = []
        for py_file in generated_project.rglob("*.py"):
            if ".git" in py_file.parts:
                continue
            try:
                ast.parse(py_file.read_text())
            except SyntaxError as e:
                failures.append(f"{py_file.relative_to(generated_project)}: {e}")
        assert failures == [], "Python syntax errors:\n" + "\n".join(failures)


class TestCMakeContent:

    def test_cmake_project_name_matches_slug(self, generated_project):
        """project() in root CMakeLists.txt uses the correct slug."""
        content = (generated_project / "CMakeLists.txt").read_text()
        assert f"project({DEFAULT_SLUG} " in content

    def test_cmake_prefix_variables(self, generated_project):
        """CMakeLists.txt uses correct prefix for all option variables."""
        content = (generated_project / "CMakeLists.txt").read_text()
        for suffix in ["BUILD_TESTS", "BUILD_PYTHON", "UNIVERSAL2", "USE_STABLE_ABI"]:
            assert f"{DEFAULT_PREFIX}_{suffix}" in content, f"Missing {DEFAULT_PREFIX}_{suffix}"

    def test_cmake_presets_valid_json(self, generated_project):
        """CMakePresets.json is valid JSON with expected preset names."""
        content = (generated_project / "CMakePresets.json").read_text()
        data = json.loads(content)
        preset_names = {p["name"] for p in data["configurePresets"]}
        assert "debug" in preset_names
        assert "release" in preset_names


class TestSWIGContent:

    def test_swig_module_name(self, generated_project):
        """.i file has exactly one %module _<slug> directive."""
        content = (generated_project / f"swig/{DEFAULT_SLUG}.i").read_text()
        directive = f"%module _{DEFAULT_SLUG}"
        count = content.count(directive)
        assert count == 1, f"Expected 1 occurrence of '{directive}', found {count}"

    def test_swig_typemap_identifiers(self, generated_project):
        """Type checker functions use the correct slug."""
        content = (generated_project / f"swig/{DEFAULT_SLUG}.i").read_text()
        expected_checkers = [
            f"_{DEFAULT_SLUG}_is_oemolbase",
            f"_{DEFAULT_SLUG}_is_oemol",
            f"_{DEFAULT_SLUG}_is_oegraphmol",
            f"_{DEFAULT_SLUG}_is_oescalargrid",
            f"_{DEFAULT_SLUG}_is_oereceptor",
        ]
        for checker in expected_checkers:
            assert checker in content, f"Missing typemap checker: {checker}"


class TestHeaderContent:

    def test_header_include_guard(self, generated_project):
        """Header uses <PREFIX>_H include guard."""
        content = (generated_project / f"include/{DEFAULT_SLUG}/{DEFAULT_SLUG}.h").read_text()
        assert f"#ifndef {DEFAULT_PREFIX}_H" in content
        assert f"#define {DEFAULT_PREFIX}_H" in content
        assert f"#endif // {DEFAULT_PREFIX}_H" in content

    def test_header_version_macros(self, generated_project):
        """Version macros match initial_version components."""
        content = (generated_project / f"include/{DEFAULT_SLUG}/{DEFAULT_SLUG}.h").read_text()
        major, minor, patch = DEFAULT_VERSION.split(".")
        assert f"{DEFAULT_PREFIX}_VERSION_MAJOR {major}" in content
        assert f"{DEFAULT_PREFIX}_VERSION_MINOR {minor}" in content
        assert f"{DEFAULT_PREFIX}_VERSION_PATCH {patch}" in content

    def test_namespace_matches_prefix(self, generated_project):
        """.h, .cpp, and .i files all use namespace <PREFIX>."""
        files = [
            f"include/{DEFAULT_SLUG}/{DEFAULT_SLUG}.h",
            f"src/{DEFAULT_SLUG}.cpp",
            f"swig/{DEFAULT_SLUG}.i",
        ]
        for rel_path in files:
            content = (generated_project / rel_path).read_text()
            assert f"namespace {DEFAULT_PREFIX}" in content, (
                f"Missing 'namespace {DEFAULT_PREFIX}' in {rel_path}"
            )


class TestVersionConsistency:

    def test_pyproject_version_consistency(self, generated_project):
        """Root pyproject.toml, python/pyproject.toml, and __init__.py share the same version."""
        root_pyproject = (generated_project / "pyproject.toml").read_text()
        inner_pyproject = (generated_project / "python/pyproject.toml").read_text()
        init_py = (generated_project / f"python/{DEFAULT_SLUG}/__init__.py").read_text()

        assert f'version = "{DEFAULT_VERSION}"' in root_pyproject
        assert f'version = "{DEFAULT_VERSION}"' in inner_pyproject
        assert f'__version__ = "{DEFAULT_VERSION}"' in init_py


class TestPythonPackage:

    def test_init_py_exports(self, generated_project):
        """__init__.py imports calculate_molecular_weight and defines __all__."""
        content = (generated_project / f"python/{DEFAULT_SLUG}/__init__.py").read_text()
        assert "calculate_molecular_weight" in content
        assert "__all__" in content

    def test_inner_pyproject_package_name(self, generated_project):
        """python/pyproject.toml has the correct package name."""
        content = (generated_project / "python/pyproject.toml").read_text()
        assert f'name = "{DEFAULT_SLUG}"' in content
        assert f'packages = ["{DEFAULT_SLUG}"]' in content


class TestConfigFiles:

    def test_build_wheels_workflow_valid_yaml(self, generated_project):
        """build-wheels.yml parses as valid YAML."""
        content = (generated_project / ".github/workflows/build-wheels.yml").read_text()
        data = yaml.safe_load(content)
        assert isinstance(data, dict)
        assert "jobs" in data

    def test_vrzn_toml_paths_exist(self, generated_project):
        """Every file referenced in vrzn.toml exists in the generated project."""
        content = (generated_project / "vrzn.toml").read_text()
        data = tomllib.loads(content)
        for location in data.get("locations", []):
            file_path = location.get("file")
            if file_path:
                assert (generated_project / file_path).is_file(), (
                    f"vrzn.toml references {file_path} but it does not exist"
                )

    def test_readme_contains_project_name(self, generated_project):
        """README.md contains the project name and description."""
        content = (generated_project / "README.md").read_text()
        assert "My OpenEye Project" in content
        assert "A C++/Python library using OpenEye Toolkits" in content


class TestVrznIntegration:

    def test_vrzn_config_valid(self, generated_project):
        """vrzn.toml is a valid vrzn configuration."""
        config_path = find_config(generated_project)
        assert config_path is not None, "vrzn config file not found"
        config = load_config(config_path)
        validate_config(config)

    def test_vrzn_all_locations_readable(self, generated_project):
        """vrzn can read a version from every configured location."""
        config_path = find_config(generated_project)
        config = load_config(config_path)
        root = config_path.parent
        locations = locations_from_config(config, root)
        assert len(locations) >= 6, f"Expected at least 6 locations, got {len(locations)}"
        for loc in locations:
            raw = loc.read_version()
            assert raw is not None, f"vrzn cannot read version from {loc.label} ({loc.file})"

    def test_vrzn_versions_agree(self, generated_project):
        """All vrzn locations that report full versions agree on the version."""
        config_path = find_config(generated_project)
        config = load_config(config_path)
        root = config_path.parent
        locations = locations_from_config(config, root)
        consensus, mismatches = check_agreement(locations)
        assert consensus is not None, "No version consensus found"
        assert str(consensus) == DEFAULT_VERSION, (
            f"Consensus {consensus} != expected {DEFAULT_VERSION}"
        )

    def test_vrzn_bump_roundtrip(self, generated_project_custom):
        """vrzn bump patch updates all locations consistently."""
        from vrzn.version import parse_version
        project = generated_project_custom()
        config_path = find_config(project)
        config = load_config(config_path)
        root = config_path.parent
        locations = locations_from_config(config, root)

        new_version = parse_version("0.2.0")
        for loc in locations:
            loc.write_version(new_version)

        for loc in locations:
            raw = loc.read_version()
            assert raw is not None, f"Version missing after write in {loc.label}"

        consensus, mismatches = check_agreement(locations)
        assert consensus is not None
        assert str(consensus) == "0.2.0"
