constexpr unsigned int K = 3;

signed int div_s1(signed int val) {
    int round = val + (1 << (K - 1));
    if (val < 0)
        round -= 1;
    return round >> K;
}

signed int div_s2(signed int val) {
    int neg = val < 0 ? 1 : 0;
    return (val + (1 << (K - 1)) - neg) >> K;
}

unsigned int div_u(unsigned int val) {
    return (val + (1 << (K - 1))) >> K;
}