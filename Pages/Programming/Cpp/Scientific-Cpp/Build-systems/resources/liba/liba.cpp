#include <fmt/core.h>
#include <liba.hpp>

void say_hello(std::string_view name) {
    fmt::print("Hello, {}!\n", name);
}
