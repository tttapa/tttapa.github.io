div_s(int):
        lea     eax, [rdi+4]
        shr     edi, 31
        sub     eax, edi
        sar     eax, 3
        ret
div_u(unsigned int):
        lea     eax, [rdi+4]
        shr     eax, 3
        ret