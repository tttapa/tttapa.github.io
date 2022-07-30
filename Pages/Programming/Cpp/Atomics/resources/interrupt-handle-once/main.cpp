// Store the value to be handled
value = 1; //                                                             ➊
value_ptr.store(&value, std::memory_order_seq_cst); //                    ➋ ▲▲▲▲
// Check if the interrupt was handled before we ran
auto h = handled.load(std::memory_order_seq_cst); //                      ➌ ▼▼▼▼
// If the interrupt ran earlier, it might not have seen our value
if (h) {
    // See if our value is still there
    auto v = value_ptr.exchange(nullptr, std::memory_order_relaxed); //   ➍
    // And handle it ourselves
    if (v)
        total.fetch_add(*v, std::memory_order_relaxed); //                ➎
}