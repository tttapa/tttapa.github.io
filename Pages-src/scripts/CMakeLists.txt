cmake_minimum_required(VERSION 3.10)

project(Pages)

################################################################################
############################   OUTPUT DIRECTORIES   ############################
################################################################################

if(NOT DEFINED CMAKE_ARCHIVE_OUTPUT_DIRECTORY)
  set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
endif()
if(NOT DEFINED CMAKE_LIBRARY_OUTPUT_DIRECTORY)
  set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
endif()
if(NOT DEFINED CMAKE_RUNTIME_OUTPUT_DIRECTORY)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
endif()

################################################################################
################################   GOOGLE TEST   ###############################
################################################################################

# https://github.com/google/googletest/blob/master/googletest/README.md#incorporating-into-an-existing-cmake-project
# <copy>
# Download and unpack googletest at configure time
configure_file(${CMAKE_CURRENT_LIST_DIR}/cmake/GoogleTest-CMakeLists.txt.in 
               googletest/CMakeLists.txt)
execute_process(COMMAND ${CMAKE_COMMAND} -G "${CMAKE_GENERATOR}" .
  RESULT_VARIABLE result
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/googletest )
if(result)
  message(FATAL_ERROR "CMake step for googletest failed: ${result}")
endif()
execute_process(COMMAND ${CMAKE_COMMAND} --build .
  RESULT_VARIABLE result
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/googletest )
if(result)
  message(FATAL_ERROR "Build step for googletest failed: ${result}")
endif()

# Prevent overriding the parent project's compiler/linker
# settings on Windows
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

# Add googletest directly to our build. This defines
# the gtest and gtest_main targets.
add_subdirectory(${CMAKE_BINARY_DIR}/googletest/googletest-src
                 ${CMAKE_BINARY_DIR}/googletest/googletest-build
                 EXCLUDE_FROM_ALL)
# </copy>
include(GoogleTest)
enable_testing()

################################################################################
#############################   COMPILER OPTIONS   #############################
################################################################################

# Use C++ 17
set(CMAKE_CXX_STANDARD 17)

# Optimize during linking stage
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE) # LTO

# Allow linking the compiled code into a shared library (for Python modules)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Compiler flags for C++
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} \
-O3 -g3 \
-Wall -Wextra -Werror \
-Wsuggest-override \
-Wno-register \
-Wno-missing-braces \
-Wno-unknown-pragmas \
-Wno-psabi \
-fdiagnostics-show-option")

if(NOT CMAKE_CROSSCOMPILING)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=native")
endif()

################################################################################
################################## EXECUTABLE ##################################
################################################################################

find_package(pybind11 REQUIRED)

add_executable(walk walk.cpp)

target_link_libraries(walk
    PUBLIC
        stdc++fs
        pybind11::embed
)