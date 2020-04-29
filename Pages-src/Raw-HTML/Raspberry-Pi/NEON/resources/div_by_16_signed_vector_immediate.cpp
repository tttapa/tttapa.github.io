#define vandq_n_u16(a, b)                                                      \
    __extension__({                                                            \
        uint16x8_t a_ = (a);                                                   \
        uint16_t b_ = ~(b);                                                    \
        __asm__("bic %0.8h, #%1" : "+w"(a_) : "i"(b_) : /* No clobbers */);    \
        a_;                                                                    \
    })

int16x8_t div_by_16(int16x8_t x) {
    uint16x8_t negative = vcltzq_s16(x); // compare less than zero
    uint16x8_t correction = vandq_n_u16(negative, 1 - 16);
    x = vsubq_s16(x, vreinterpretq_s16_u16(correction));
    return vshrq_n_s16(x, 4); // 16 = 2⁴
}