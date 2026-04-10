include(FetchContent)

FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.15.2
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(googletest)

add_executable({{ cookiecutter.project_slug }}_tests
    test_{{ cookiecutter.project_slug }}.cpp
)

target_link_libraries({{ cookiecutter.project_slug }}_tests
    PRIVATE
        {{ cookiecutter.project_slug }}
        GTest::gtest_main
)

include(GoogleTest)
gtest_discover_tests({{ cookiecutter.project_slug }}_tests)
