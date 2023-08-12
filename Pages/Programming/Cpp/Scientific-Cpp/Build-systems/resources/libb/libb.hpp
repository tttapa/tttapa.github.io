#pragma once

#include <span>
#include <string_view>

/// Print a greeting message for each of the names in the array.
void greet_multiple(std::span<const std::string_view> names);
