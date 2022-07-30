if (value_ready.load(std::memory_order_acquire)) //                       ➌ ▼▼▼▼
    assert(value == 42); //                                               ➍