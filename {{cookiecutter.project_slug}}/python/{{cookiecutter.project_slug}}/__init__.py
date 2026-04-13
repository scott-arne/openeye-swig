"""
{{ cookiecutter.project_name }} - {{ cookiecutter.project_description }}
"""

import os
import re
import warnings

__version__ = "{{ cookiecutter.initial_version }}"
__version_info__ = ({{ cookiecutter.initial_version.replace('.', ', ') }})


def _ensure_library_compat():
    """Create compatibility symlinks when OpenEye library versions differ from build time.

    When this package is built with shared OpenEye libraries, the compiled extension
    records the exact versioned library filenames (e.g., liboechem-4.3.0.1.dylib).
    If the user upgrades openeye-toolkits, these filenames change and the dynamic
    linker fails to load the extension.

    This function detects version mismatches and creates symlinks from the expected
    (build-time) library names to the actual (runtime) library files.
    """
    try:
        from . import _build_info
    except ImportError:
        return False

    if getattr(_build_info, 'OPENEYE_LIBRARY_TYPE', 'STATIC') != 'SHARED':
        return False

    expected_libs = getattr(_build_info, 'OPENEYE_EXPECTED_LIBS', [])
    if not expected_libs:
        return False

    try:
        from openeye import libs
        oe_lib_dir = libs.FindOpenEyeDLLSDirectory()
    except (ImportError, Exception):
        return False

    if not os.path.isdir(oe_lib_dir):
        return False

    pkg_dir = os.path.dirname(__file__)
    created_any = False

    for expected_name in expected_libs:
        if os.path.exists(os.path.join(oe_lib_dir, expected_name)):
            continue

        symlink_path = os.path.join(pkg_dir, expected_name)
        if os.path.islink(symlink_path):
            if os.path.exists(symlink_path):
                continue
            try:
                os.unlink(symlink_path)
            except OSError:
                continue
        elif os.path.exists(symlink_path):
            continue

        match = re.match(r'(lib\w+?)(-[\d.]+)?(\.[\d.]*\w+)$', expected_name)
        if not match:
            continue
        base_name = match.group(1)

        actual_path = None
        for f in os.listdir(oe_lib_dir):
            if f.startswith(base_name + '-') or f.startswith(base_name + '.'):
                actual_path = os.path.join(oe_lib_dir, f)
                break

        if actual_path:
            try:
                os.symlink(actual_path, os.path.join(pkg_dir, expected_name))
                created_any = True
            except OSError:
                pass

    return created_any


def _preload_shared_libs():
    """Preload OpenEye shared libraries so the C extension can find them.

    On Linux, auditwheel excludes OpenEye libraries from the wheel but the
    resulting RUNPATH does not include the OpenEye library directory.
    On macOS, @rpath references may not resolve without preloading.
    """
    import ctypes
    import sys
    if sys.platform not in ('linux', 'darwin'):
        return

    try:
        from . import _build_info
    except ImportError:
        return

    if getattr(_build_info, 'OPENEYE_LIBRARY_TYPE', 'STATIC') != 'SHARED':
        return

    try:
        from openeye import libs
        oe_lib_dir = libs.FindOpenEyeDLLSDirectory()
    except (ImportError, Exception):
        return

    if not os.path.isdir(oe_lib_dir):
        return

    ext = '.dylib' if sys.platform == 'darwin' else '.so'
    for f in sorted(os.listdir(oe_lib_dir)):
        if f.endswith(ext) or (ext == '.so' and '.so.' in f):
            try:
                ctypes.CDLL(os.path.join(oe_lib_dir, f), mode=ctypes.RTLD_GLOBAL)
            except OSError:
                pass

    pkg_dir = os.path.dirname(__file__)
    expected_libs = getattr(_build_info, 'OPENEYE_EXPECTED_LIBS', [])
    for lib_name in expected_libs:
        symlink = os.path.join(pkg_dir, lib_name)
        if os.path.islink(symlink):
            try:
                ctypes.CDLL(symlink, mode=ctypes.RTLD_GLOBAL)
            except OSError:
                pass


def _preload_bundled_libs():
    """Preload libraries bundled by auditwheel from the .libs directory.

    auditwheel repair bundles non-manylinux dependencies (e.g. libraries
    from FetchContent or system packages) into a ``<package>.libs/``
    directory next to the package. The bundled copies have hashed filenames
    and must be loaded before the C extension to satisfy its DT_NEEDED
    entries.

    Libraries may have inter-dependencies, so we do multiple passes
    until no new libraries can be loaded.
    """
    import sys
    if sys.platform != 'linux':
        return

    import ctypes
    pkg_name = __name__
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    site_dir = os.path.dirname(pkg_dir)
    for libs_name in (f'{pkg_name}.libs', f'.{pkg_name}.libs'):
        libs_dir = os.path.join(site_dir, libs_name)
        if not os.path.isdir(libs_dir):
            continue
        remaining = [
            os.path.join(libs_dir, f)
            for f in sorted(os.listdir(libs_dir))
            if '.so' in f
        ]
        # Multi-pass: keep retrying until no progress (handles dep ordering)
        while remaining:
            failed = []
            for lib_path in remaining:
                try:
                    ctypes.CDLL(lib_path, mode=ctypes.RTLD_GLOBAL)
                except OSError:
                    failed.append(lib_path)
            if len(failed) == len(remaining):
                break  # No progress, stop
            remaining = failed


def _check_openeye_version():
    """Check that the OpenEye version matches what was used at build time."""
    try:
        from . import _build_info
    except ImportError:
        return

    if getattr(_build_info, 'OPENEYE_LIBRARY_TYPE', 'STATIC') != 'SHARED':
        return

    build_version = getattr(_build_info, 'OPENEYE_BUILD_VERSION', None)
    if not build_version:
        return

    try:
        from openeye import oechem
        runtime_version = oechem.OEToolkitsGetRelease()
        if runtime_version and build_version:
            build_parts = build_version.split('.')[:3]
            runtime_parts = runtime_version.split('.')[:3]
            if build_parts != runtime_parts:
                warnings.warn(
                    f"OpenEye version mismatch: {{ cookiecutter.project_slug }} was built with "
                    f"OpenEye Toolkits {build_version} but runtime has {runtime_version}. "
                    f"This may cause compatibility issues.",
                    RuntimeWarning
                )
    except ImportError:
        warnings.warn(
            "openeye-toolkits package not found. "
            "Install with: pip install openeye-toolkits",
            ImportWarning
        )


_ensure_library_compat()
_preload_shared_libs()
_preload_bundled_libs()
_check_openeye_version()

from .{{ cookiecutter.project_slug }} import (
    calculate_molecular_weight,
)

__all__ = [
    "__version__",
    "__version_info__",
    "calculate_molecular_weight",
]
