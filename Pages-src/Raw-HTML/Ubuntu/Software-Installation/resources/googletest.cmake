enable_testing()
find_package(GTest REQUIRED)
include(GoogleTest)

add_executable(test-exe test.cpp) # test.cpp contains TEST(...) cases
target_link_libraries(test-exe PRIVATE GTest::gtest_main)

if(NOT CMAKE_CROSSCOMPILING)
    gtest_discover_tests(test-exe)
endif()