int16x8_t div_by_16_round(int16x8_t x) {
    uint16x8_t sign = vshrq_n_u16(vreinterpretq_u16_s16(x), 15); // sign bit
    x = vqsubq_s16(x, vreinterpretq_s16_u16(sign)); // subtract 1 if < 0
    return vrshrq_n_s16(x, 4);                      // 16 = 2⁴
}