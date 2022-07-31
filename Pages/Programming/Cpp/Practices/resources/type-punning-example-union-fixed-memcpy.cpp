float x = 12.34f;
uint8_t bytes[sizeof(x)];
std::memcpy(bytes, x, sizeof(x));