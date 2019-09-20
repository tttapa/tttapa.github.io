constexpr unsigned int K = 3;

signed int div_s(signed int val) {
    int neg = val < 0 ? 1 : 0;
    int shiftval = (val + (1 << (K - 1)) - neg) >> K;
    return shiftval;
}

unsigned int div_u(unsigned int val) {
    return (val + (1 << (K - 1))) >> K;
}