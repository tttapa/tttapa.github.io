// Notify the main thread that the interrupt ran
handled.store(true, std::memory_order_seq_cst); //                        ➏ ▲▲▲▲
// Read the value from the main thread
auto v = value_ptr.exchange(nullptr, std::memory_order_seq_cst); //       ➐ ▼▼▼▼
// Handle it
if (v)
    total.fetch_add(*v, std::memory_order_relaxed); //                    ➑
