include(OpenEyeSWIG)

openeye_add_swig_module(
    NAME {{ cookiecutter.project_slug }}
    SWIG_FILE {{ cookiecutter.project_slug }}.i
    LINK_LIBS {{ cookiecutter.project_slug }}
    PYTHON_OUTPUT_DIR ${CMAKE_SOURCE_DIR}/python/{{ cookiecutter.project_slug }}
    STABLE_ABI ${{ '{' }}{{ cookiecutter.project_prefix }}_USE_STABLE_ABI}
    SWIG_FLAGS "-doxygen"
    EXPECTED_LIB_VARS
        OECHEM_LIBRARY OESYSTEM_LIBRARY OEPLATFORM_LIBRARY
        OEMATH_LIBRARY OEZSTD_LIBRARY
    INIT_PY ${CMAKE_SOURCE_DIR}/python/{{ cookiecutter.project_slug }}/__init__.py
)
