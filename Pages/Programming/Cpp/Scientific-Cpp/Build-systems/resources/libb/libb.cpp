#include <liba.hpp>
#include <libb.hpp>

void greet_multiple(std::span<const std::string_view> names) {
    for (auto name : names)
        say_hello(name);
}
