# Dependencies and dynamic section of a shared library
readelf -d libfile.so
# List of symbols in shared library (1)
nm -CD --defined-only --size-sort libfile.so
# List of symbols in shared library (2)
readelf --wide --symbols --demangle libfile.so
# Filter symbols and prevent line wrapping
readelf --wide --symbols --demangle libfile.so | grep name | bat --wrap=never
