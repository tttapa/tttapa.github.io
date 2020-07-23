div_s1(int):
        sbrc r25,7  # Skip if Bit in Register is Cleared: val >= 0
        rjmp .L2
                    # val >= 0
        adiw r24,4  # Add Immediate to Word: val + (1 << (K - 1)) = val + 4
        asr r25     # Arithmetic Shift Right: shift high byte (preserve sign)
        ror r24     # Rotate Right through Carry: shift low byte
        asr r25     # Two more times
        ror r24
        asr r25
        ror r24
        ret
.L2:                
                    # val < 0
        adiw r24,3  # Add Immediate to Word: val + (1 << (K - 1)) - 1 = val + 3
        asr r25     # Arithmetic Shift Right: shift high byte (preserve sign)
        ror r24     # Rotate Right through Carry: shift low byte
        asr r25     # Two more times
        ror r24
        asr r25
        ror r24
        ret

div_s2(int):
        movw r18,r24
        subi r18,-4   # Subtract immediate: val + (1 << (K - 1)) = val + 4
        sbci r19,-1   # Subtract Immediate with Carry: (low byte)
        mov r24,r25
        rol r24       # Rotate Left through Carry: C flag is now sign bit
        clr r24       # Clear Register
        rol r24       # Rotate Left through Carry: original sign bit is now lsb
        movw r20,r18
        sub r20,r24   # Subtract without Carry: val + 4 - neg
        sbc r21,__zero_reg__  # Subtract with Carry: (low byte)
        movw r24,r20
        asr r25       # Arithmetic Shift Right: shift high byte (preserve sign)
        ror r24       # Rotate Right through Carry: shift low byte
        asr r25       # Two more times
        ror r24
        asr r25
        ror r24
        ret

div_u(unsigned int):
        adiw r24,4  # Add Immediate to Word: val + (1 << (K - 1)) = val + 4
        lsr r25     # Logical Shift Right: shift high byte (no sign extension)
        ror r24     # Rotate Right through Carry: shift low byte
        lsr r25     # Two more times
        ror r24
        lsr r25
        ror r24
        ret