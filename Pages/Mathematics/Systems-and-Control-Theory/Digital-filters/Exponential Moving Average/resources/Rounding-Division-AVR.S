__zero_reg__ = 1
div_s(int):
        mov r18,r24
        mov r19,r25
        subi r18,-4
        sbci r19,-1
        mov r24,r25
        rol r24
        clr r24
        rol r24
        mov r20,r18
        mov r21,r19
        sub r20,r24
        sbc r21,__zero_reg__
        mov r24,r20
        mov r25,r21
        asr r25
        ror r24
        asr r25
        ror r24
        asr r25
        ror r24
        ret
div_u(unsigned int):
        adiw r24,4
        lsr r25
        ror r24
        lsr r25
        ror r24
        lsr r25
        ror r24
        ret