std::atomic_bool handled{false};
unsigned value = 0;
std::atomic<const unsigned *> value_ptr{nullptr};
std::atomic_uint total{0};