cmake_minimum_required(VERSION 3.10)

project(Pages CXX)

# OUTPUT DIRECTORIES
# ------------------------------------------------------------------------------

if(NOT DEFINED CMAKE_ARCHIVE_OUTPUT_DIRECTORY)
  set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
endif()
if(NOT DEFINED CMAKE_LIBRARY_OUTPUT_DIRECTORY)
  set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
endif()
if(NOT DEFINED CMAKE_RUNTIME_OUTPUT_DIRECTORY)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
endif()

# COMPILER OPTIONS
# ------------------------------------------------------------------------------

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

# EXECUTABLE
# ------------------------------------------------------------------------------

find_package(pybind11 REQUIRED)

find_package(Threads REQUIRED)

add_executable(page-builder page-builder.cpp)
target_link_libraries(page-builder
    PUBLIC
        stdc++fs
        pybind11::embed
        Threads::Threads
)