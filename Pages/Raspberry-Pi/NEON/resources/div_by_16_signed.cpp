int16_t div_by_16_a(int16_t x) {
    return x / 16;
}

int16_t div_by_16_b(int16_t x) {
    if (x < 0)
        x += 16 - 1;
    return x >> 4; // 16 = 2⁴
}