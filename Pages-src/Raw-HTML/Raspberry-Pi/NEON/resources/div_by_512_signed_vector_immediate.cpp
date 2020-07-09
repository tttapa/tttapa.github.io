#define vandq_n_high_u16(a, b)                                                 \
    __extension__({                                                            \
        uint16x8_t a_ = (a);                                                   \
        uint16_t b_ = (~(b)) >> 8;                                             \
        __asm__("bic %0.8h, #%1, LSL #8" : "+w"(a_) : "i"(b_) :);              \
        a_;                                                                    \
    })

int16x8_t div_by_512(int16x8_t x) {
    uint16x8_t negative = vcltzq_s16(x); // compare less than zero
    uint16x8_t correction = vandq_n_high_u16(negative, 512 - 1);
    x = vaddq_s16(x, vreinterpretq_s16_u16(correction));
    return vshrq_n_s16(x, 9); // 512 = 2⁹
}