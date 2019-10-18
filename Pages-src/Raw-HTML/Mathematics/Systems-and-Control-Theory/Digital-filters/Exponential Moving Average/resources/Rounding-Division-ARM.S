div_s1(int):
        mvn     w1, w0
        add     w0, w0, w1, lsr 31
        add     w0, w0, 3
        asr     w0, w0, 3
        ret

div_s2(int):
        add     w1, w0, 4
        sub     w0, w1, w0, lsr 31
        asr     w0, w0, 3
        ret

div_u(unsigned int):
        add     w0, w0, 4
        lsr     w0, w0, 3
        ret