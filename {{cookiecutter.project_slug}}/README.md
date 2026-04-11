# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

This project provides a C++ library with Python bindings built using SWIG and
[OpenEye Toolkits](https://www.eyesopen.com/). Molecules created with
`openeye.oechem` in Python pass natively to C++ without serialization.

## Prerequisites

- **OpenEye C++ SDK** -- Headers and libraries (download from
  [OpenEye](https://www.eyesopen.com/))
- **OpenEye Python Toolkits** -- `pip install openeye-toolkits`
- **CMake** >= 3.16
- **SWIG** >= 4.0
- **Python** >= {{ cookiecutter.python_min_version }}

## Getting Started

### 1. Configure the OpenEye SDK Path

Create a local presets file that points CMake to your OpenEye C++ SDK:

```bash
cp CMakePresets.json CMakeUserPresets.json
```

Edit `CMakeUserPresets.json` and replace `/path/to/openeye/sdk` with the actual
path to your OpenEye C++ SDK installation (the directory containing `include/`
and `lib/`). This file is gitignored so it won't be committed.

### 2. Build the C++ Library and SWIG Bindings

```bash
cmake --preset debug
cmake --build build-debug
```

This builds the static C++ library, generates the SWIG wrapper, and places the
compiled Python extension module in `python/{{ cookiecutter.project_slug }}/`.

To build in release mode:

```bash
cmake --preset release
cmake --build build-release
```

### 3. Install for Development

Install the Python package in editable mode so changes to the C++ code are
reflected after rebuilding:

```bash
pip install --config-settings editable_mode=compat -e python/
```

### 4. Run Tests

C++ tests (built automatically with the debug preset):

```bash
cd build-debug && ctest --output-on-failure
```

Python tests:

```bash
pytest tests/python/ -v
```

The Python tests verify that molecules created with `openeye.oechem.OEGraphMol`
pass correctly to the C++ `calculate_molecular_weight` function.

## Usage

```python
from openeye import oechem
from {{ cookiecutter.project_slug }} import calculate_molecular_weight

mol = oechem.OEGraphMol()
oechem.OESmilesToMol(mol, "CC(=O)OC1=CC=CC=C1C(=O)O")  # aspirin

mw = calculate_molecular_weight(mol)
print(f"Molecular weight: {mw:.2f}")  # 180.16
```

The `OEGraphMol` object passes directly from Python to C++ via cross-runtime
SWIG typemaps. No SMILES round-trip or manual pointer handling is needed.

## Project Structure

```
{{ cookiecutter.project_slug }}/
    CMakeLists.txt                  # Build configuration
    CMakePresets.json               # CMake presets (copy to CMakeUserPresets.json)
    pyproject.toml                  # Package metadata + [tool.oe-build] config
    vrzn.toml                       # Version locations for vrzn
    include/{{ cookiecutter.project_slug }}/
        {{ cookiecutter.project_slug }}.h               # Public C++ header
    src/
        {{ cookiecutter.project_slug }}.cpp             # C++ implementation
    swig/
        {{ cookiecutter.project_slug }}.i               # SWIG interface with OEMolBase typemaps
        CMakeLists.txt              # SWIG module build rules
    python/
        pyproject.toml              # Setuptools config for editable installs
        {{ cookiecutter.project_slug }}/
            __init__.py             # Python package (imports, compat layer)
    scripts/
        build_python.py             # Build distributable wheels
    tests/
        cpp/
            CMakeLists.txt          # C++ test build rules
            test_{{ cookiecutter.project_slug }}.cpp     # C++ unit tests
        python/
            conftest.py             # Pytest fixtures (molecule helpers)
            test_{{ cookiecutter.project_slug }}.py      # Python tests
    .github/workflows/
        build-wheels.yml            # CI: multi-platform wheel builds
```

## Adding New Functions

The scaffolded `calculate_molecular_weight` function demonstrates the pattern for
wrapping C++ code that operates on OpenEye molecules. To add your own functions:

**1. Declare in the header** (`include/{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}.h`):

```cpp
namespace {{ cookiecutter.project_prefix }} {

double my_function(const OEChem::OEMolBase& mol);

} // namespace {{ cookiecutter.project_prefix }}
```

**2. Implement** (`src/{{ cookiecutter.project_slug }}.cpp` or a new `.cpp` file):

```cpp
namespace {{ cookiecutter.project_prefix }} {

double my_function(const OEChem::OEMolBase& mol) {
    // Your implementation using OpenEye C++ API
}

} // namespace {{ cookiecutter.project_prefix }}
```

If you add new `.cpp` files, add them to the `{{ cookiecutter.project_prefix }}_SOURCES` list in
`CMakeLists.txt`.

**3. Expose in SWIG** (`swig/{{ cookiecutter.project_slug }}.i`), under the "Wrapped API" section:

```swig
namespace {{ cookiecutter.project_prefix }} {
double my_function(const OEChem::OEMolBase& mol);
}
```

Any function accepting `OEMolBase&` or `const OEMolBase&` will automatically use
the cross-runtime typemaps.

**4. Import in Python** (`python/{{ cookiecutter.project_slug }}/__init__.py`):

```python
from .{{ cookiecutter.project_slug }} import (
    calculate_molecular_weight,
    my_function,
)
```

**5. Rebuild and test:**

```bash
cmake --build build-debug
pytest tests/python/ -v
```

## Building Wheels

### Local Build

The `scripts/build_python.py` script builds a distributable wheel. It reads
project-specific settings from the `[tool.oe-build]` section of `pyproject.toml`,
so the script itself never needs modification.

```bash
python scripts/build_python.py --openeye-root /path/to/openeye/sdk --verbose
```

The built wheel will be placed in `dist/`. On macOS, the script automatically
runs `delocate` to bundle non-OpenEye dependencies and sets the correct RPATH
for OpenEye shared libraries.

Options:

```
--openeye-root PATH    Path to OpenEye C++ SDK (or set OPENEYE_ROOT env var)
--python PATH          Python executable to use
--clean                Clean dist/ before building
--upload               Upload to PyPI after building
--test-upload          Upload to TestPyPI instead
--verbose              Show build commands
```

If `--openeye-root` is not provided, the script checks the `OPENEYE_ROOT`
environment variable and then `CMakePresets.json` / `CMakeUserPresets.json`.

### CI Builds

The included GitHub Actions workflow (`.github/workflows/build-wheels.yml`)
builds wheels on:

- Linux x86_64 (Rocky Linux 8, manylinux_2_28)
- Linux aarch64 (Rocky Linux 9, manylinux_2_34)
- macOS arm64 (universal2)

It triggers on version tags (`v*`) and `workflow_dispatch`. Wheels are published
to PyPI via trusted publishing on tag pushes.

**Required GitHub Secrets:**

| Secret | Description |
|--------|-------------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | GCP Workload Identity Federation provider |
| `GCP_SERVICE_ACCOUNT` | GCP service account for SDK downloads |

The OpenEye C++ SDK and license file are downloaded from a GCS bucket during CI
(the bucket name is configured during project setup).

## CMake Options

| Option | Default | Description |
|--------|---------|-------------|
| `{{ cookiecutter.project_prefix }}_BUILD_TESTS` | ON | Build C++ tests |
| `{{ cookiecutter.project_prefix }}_BUILD_PYTHON` | ON | Build Python SWIG bindings |
| `{{ cookiecutter.project_prefix }}_UNIVERSAL2` | OFF | Build macOS universal2 binary |
| `{{ cookiecutter.project_prefix }}_USE_STABLE_ABI` | OFF | Use Python stable ABI (abi3) |

## Tools

This project uses several tools to manage the build, packaging, and versioning:

| Tool | Purpose |
|------|---------|
| [CMake](https://cmake.org/) | Build system for the C++ library and SWIG bindings |
| [SWIG](https://www.swig.org/) | Generates Python bindings from C++ headers |
| [scikit-build-core](https://scikit-build-core.readthedocs.io/) | Python build backend that delegates to CMake |
| [cmake-openeye](https://github.com/scott-arne/cmake-openeye) | CMake modules for finding the OpenEye SDK and building SWIG targets |
| [vrzn](https://github.com/scott-arne/vrzn) | Keeps version numbers in sync across all project files |
| [delocate](https://github.com/matthew-brett/delocate) | Bundles shared libraries into macOS wheels |
| [auditwheel](https://github.com/pypa/auditwheel) | Bundles shared libraries into Linux wheels |
| [pytest](https://docs.pytest.org/) | Test framework for the Python test suite |

## Version Management

This project uses [vrzn](https://github.com/scott-arne/vrzn) to keep version
numbers consistent across all project files. The `vrzn.toml` configuration
tracks six version locations:

| File | Location Type |
|------|---------------|
| `pyproject.toml` | `[project] version` |
| `python/pyproject.toml` | `[project] version` |
| `python/{{ cookiecutter.project_slug }}/__init__.py` | `__version__` |
| `python/{{ cookiecutter.project_slug }}/__init__.py` | `__version_info__` |
| `CMakeLists.txt` | `project(... VERSION ...)` |
| `include/{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}.h` | `#define` version macros |

Common commands:

```bash
vrzn get          # Show current version in all tracked locations
vrzn bump patch   # Bump patch version (e.g. 0.1.0 -> 0.1.1)
vrzn bump minor   # Bump minor version (e.g. 0.1.0 -> 0.2.0)
vrzn set 1.0.0    # Set an explicit version everywhere
```

Install vrzn with:

```bash
pip install vrzn
```

## License

{{ cookiecutter.license }}
