uint16_t div_by_16_a(uint16_t x) {
    return x / 16;
}

uint16_t div_by_16_b(uint16_t x) {
    return x >> 4; // 16 = 2⁴
}