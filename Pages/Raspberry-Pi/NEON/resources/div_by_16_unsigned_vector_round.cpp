uint16x8_t div_by_16_round(uint16x8_t x) {
    return vrshrq_n_u16(x, 4); // 16 = 2⁴
}