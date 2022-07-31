uint8_t bytes[] {0xA4, 0x70, 0x45, 0x41};
float x = *reinterpret_cast<float *>(bytes); // Error: Undefined Behavior