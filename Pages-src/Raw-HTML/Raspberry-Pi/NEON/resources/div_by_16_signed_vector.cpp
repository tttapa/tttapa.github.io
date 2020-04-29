int16x8_t div_by_16(int16x8_t x) {
    int16x8_t negative = vcltzq_s16(x); // compare less than zero
    int16x8_t correction = vdupq_n_s16(16 - 1);
    correction = vandq_s16(negative, correction); // only add correction if < 0
    x = vaddq_s16(x, correction);
    return vshrq_n_s16(x, 4); // 16 = 2⁴
}