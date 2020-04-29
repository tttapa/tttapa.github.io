uint8x8_t div_by_255_round(uint16x8_t x) {
    // Add the rounding constant
    x = vaddq_u16(x, vdupq_n_u16(1 << 7));
    // Multiply by 0x8080 as 32-bit integers (high and low words separately)
    uint32x4_t h = vmull_high_n_u16(x, 0x8080);
    uint32x4_t l = vmull_n_u16(vget_low_u16(x), 0x8080);
    // Extract the 16 high bits of all 32-bit products (division by 0x10000)
    x = vuzp2q_u16(vreinterpretq_u16_u32(l), vreinterpretq_u16_u32(h));
    // Divide by 0x80 and narrow from 16 bits to 8 bits
    return vshrn_n_u16(x, 7);
}