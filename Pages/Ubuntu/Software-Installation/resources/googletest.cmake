enable_testing()
find_package(GTest REQUIRED)
include(GoogleTest)

add_executable(test-exe test.cpp)
target_link_libraries(test-exe PUBLIC GTest::gtest_main)

if(NOT CMAKE_CROSSCOMPILING)
    gtest_discover_tests(test-exe)
endif()