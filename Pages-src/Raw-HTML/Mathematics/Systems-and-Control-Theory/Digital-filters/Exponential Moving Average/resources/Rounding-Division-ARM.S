div_s(int):
        add     r3, r0, #4
        sub     r0, r3, r0, lsr #31
        asr     r0, r0, #3
        bx      lr
div_u(unsigned int):
        add     r0, r0, #4
        lsr     r0, r0, #3
        bx      lr