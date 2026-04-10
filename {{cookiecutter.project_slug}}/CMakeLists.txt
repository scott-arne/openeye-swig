cmake_minimum_required(VERSION 3.16)

if(POLICY CMP0144)
    cmake_policy(SET CMP0144 NEW)
endif()

project({{ cookiecutter.project_slug }} VERSION {{ cookiecutter.initial_version }} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Options
option({{ cookiecutter.project_prefix }}_BUILD_TESTS "Build tests" ON)
option({{ cookiecutter.project_prefix }}_BUILD_PYTHON "Build Python bindings" ON)
option({{ cookiecutter.project_prefix }}_UNIVERSAL2 "Build universal2 binary for macOS" OFF)
option({{ cookiecutter.project_prefix }}_USE_STABLE_ABI "Use Python stable ABI" OFF)

if(APPLE AND {{ cookiecutter.project_prefix }}_UNIVERSAL2)
    set(CMAKE_OSX_ARCHITECTURES "x86_64;arm64" CACHE STRING "Build architectures" FORCE)
    set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0" CACHE STRING "Minimum macOS version" FORCE)
endif()

# Dependencies
include(FetchContent)

FetchContent_Declare(
    cmake_openeye
    GIT_REPOSITORY https://github.com/scott-arne/cmake-openeye.git
    GIT_TAG {{ cookiecutter.cmake_openeye_version }}
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(cmake_openeye)
list(APPEND CMAKE_MODULE_PATH "${cmake_openeye_SOURCE_DIR}")

if({{ cookiecutter.project_prefix }}_BUILD_PYTHON)
    find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
    find_package(SWIG 4.0)
endif()

if(OPENEYE_USE_SHARED)
    find_package(OpenEyePython REQUIRED)
endif()

find_package(OpenEye REQUIRED)

# Library
set({{ cookiecutter.project_prefix }}_SOURCES
    src/{{ cookiecutter.project_slug }}.cpp
)

add_library({{ cookiecutter.project_slug }} ${{ '{' }}{{ cookiecutter.project_prefix }}_SOURCES})

set_target_properties({{ cookiecutter.project_slug }} PROPERTIES POSITION_INDEPENDENT_CODE ON)

target_include_directories({{ cookiecutter.project_slug }}
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_link_libraries({{ cookiecutter.project_slug }}
    PUBLIC
        OpenEye::OEChem
)

# Tests
if({{ cookiecutter.project_prefix }}_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Python bindings
if({{ cookiecutter.project_prefix }}_BUILD_PYTHON AND SWIG_FOUND)
    add_subdirectory(swig)
endif()

# Install
install(TARGETS {{ cookiecutter.project_slug }}
    EXPORT {{ cookiecutter.project_slug }}-targets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(DIRECTORY include/{{ cookiecutter.project_slug }} DESTINATION include)

install(EXPORT {{ cookiecutter.project_slug }}-targets
    FILE {{ cookiecutter.project_prefix }}Targets.cmake
    NAMESPACE {{ cookiecutter.project_prefix }}::
    DESTINATION lib/cmake/{{ cookiecutter.project_slug }}
)
