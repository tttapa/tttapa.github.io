#pragma once

#include <span>
#include <string_view>

/// Print a greeting for each of the names in the array.
void greet_many(std::span<const std::string_view> names);
