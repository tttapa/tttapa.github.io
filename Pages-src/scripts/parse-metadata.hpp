#pragma once

#include <map>
#include <string>

std::map<std::string, std::string> parse_metadata(const char *contents,
                                                  const char *path);