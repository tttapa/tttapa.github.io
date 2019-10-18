div_s1(int):
        mov     eax, edi
        not     eax
        shr     eax, 31
        lea     eax, [rax+3+rdi]
        sar     eax, 3
        ret

div_s2(int):
        lea     eax, [rdi+4]
        shr     edi, 31
        sub     eax, edi
        sar     eax, 3
        ret

div_u(unsigned int):
        lea     eax, [rdi+4]
        shr     eax, 3
        ret