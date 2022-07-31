float y = number;
auto  i = std::bit_cast<uint32_t>(y);   // evil floating point bit level hacking
i       = 0x5f3759df - (i >> 1);        // what the fuck? 
y       = std::bit_cast<float>(i);