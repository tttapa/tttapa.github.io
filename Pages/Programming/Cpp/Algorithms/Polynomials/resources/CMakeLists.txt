cmake_minimum_required(VERSION 3.23)
project(Polynomials CXX)

find_package(Eigen3 CONFIG REQUIRED)

add_library(polynomials INTERFACE)
target_include_directories(polynomials INTERFACE include)
target_link_libraries(polynomials INTERFACE Eigen3::Eigen)
set(POLY_PCH <Eigen/Dense> <Eigen/LU> <Eigen/QR> <Eigen/SVD>)
string(REPLACE > "$<ANGLE-R>" POLY_PCH "${POLY_PCH}")
target_precompile_headers(polynomials INTERFACE
    "$<BUILD_INTERFACE:${POLY_PCH}>")
target_compile_features(polynomials INTERFACE cxx_std_17)

add_executable(poly_eval "src/poly_eval.cpp")
target_link_libraries(poly_eval PRIVATE polynomials)

add_executable(poly_interp "src/poly_interp.cpp")
target_link_libraries(poly_interp PRIVATE polynomials)
target_precompile_headers(poly_interp REUSE_FROM poly_eval) # TODO: <?>