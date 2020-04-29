uint8x8_t div_by_256(uint16x8_t x) { 
    return vshrn_n_u16(x, 8); // 256 = 2⁸
}
