float y = number;
uint32_t i;
static_assert(sizeof(i) == sizeof(y), "error: different sizes");
std::memcpy(&i, &y, sizeof(i));         // evil floating point bit level hacking
i = 0x5f3759df - (i >> 1);              // what the fuck? 
std::memcpy(&y, &i, sizeof(y));