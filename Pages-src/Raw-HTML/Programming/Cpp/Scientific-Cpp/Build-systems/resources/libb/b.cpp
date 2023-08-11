#include <a.hpp>
#include <b.hpp>

void greet_many(std::span<const std::string_view> names) {
    for (auto name : names)
        say_hello(name);
}
