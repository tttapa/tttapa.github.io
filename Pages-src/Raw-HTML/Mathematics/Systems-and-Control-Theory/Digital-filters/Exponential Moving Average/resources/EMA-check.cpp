EMA<5, int_fast16_t, uint_fast16_t> filter;
static_assert(filter.supports_range(-1024, 1023),
              "use a wider state or input type, or a smaller shift factor");