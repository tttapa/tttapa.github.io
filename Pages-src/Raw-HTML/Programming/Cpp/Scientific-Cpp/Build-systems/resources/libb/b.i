# 1 "libb/b.cpp"
# 1 "liba/a.hpp" 1

# 1 "/usr/include/c++/11/string_view" 1 3
/* Thousands of lines of standard library code omitted */
# 4 "liba/a.hpp" 2
                                                                  // All comments were removed by the preprocessor
# 6 "liba/a.hpp"
void say_hello(std::string_view name);                            // This is line 6 of a.hpp
# 2 "libb/b.cpp" 2
# 1 "libb/b.hpp" 1

# 1 "/usr/include/c++/11/span" 1 3
/* More standard library code omitted */
# 4 "libb/b.hpp" 2

# 7 "libb/b.hpp"
void greet_many(std::span<const std::string_view> names);         // This is line 7 of b.hpp
# 3 "libb/b.cpp" 2

void greet_many(std::span<const std::string_view> names) {        // This is line 4 of b.cpp
    for (auto name : names)
        say_hello(name);
}
