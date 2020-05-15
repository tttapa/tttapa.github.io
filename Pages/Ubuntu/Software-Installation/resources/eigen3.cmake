find_package(Eigen3 REQUIRED)

add_executable(eigen-demo main.cpp)
target_link_libraries(eigen-demo PRIVATE Eigen3::Eigen)