cmake_minimum_required(VERSION 3.12)

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

# Use C++ 20
set(CMAKE_CXX_STANDARD 20)

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

find_program(pybind11_config pybind11-config)
if (pybind11_config)
    execute_process(COMMAND ${pybind11_config} --cmakedir
                    OUTPUT_VARIABLE pybind11_ROOT_OUTPUT
                    OUTPUT_STRIP_TRAILING_WHITESPACE)
    message(STATUS "Found pybind11: ${pybind11_ROOT_OUTPUT}")
    set(pybind11_DIR ${pybind11_ROOT_OUTPUT} CACHE PATH "pybind11 path" FORCE)
endif()

find_package(pybind11 REQUIRED)
find_package(Threads REQUIRED)

add_executable(page-builder page-builder.cpp parse-metadata.cpp)
target_include_directories(page-builder PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(page-builder
    PUBLIC
        stdc++fs
        pybind11::embed
        Threads::Threads
)