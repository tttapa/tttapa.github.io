#include <fmt/core.h>
#include <a.hpp>

void say_hello(std::string_view name) {
    fmt::print("Hello, {}!\n", name);
}
