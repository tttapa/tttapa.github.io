#include <arm_neon.h>

uint16x4_t div_by_16(uint16x4_t x) {
    return vshr_n_u16(x, 4); // 16 = 2⁴
}

uint16x8_t div_by_16(uint16x8_t x) {
    return vshrq_n_u16(x, 4); // 16 = 2⁴
}