union {
    float x;
    std::byte bytes[sizeof(x)];
} u;
u.x = 12.34f;
write_to_file(u.bytes, sizeof(u.bytes)); // Error: Undefined Behavior
