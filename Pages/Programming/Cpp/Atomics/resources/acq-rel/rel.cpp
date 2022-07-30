value = 42; //                                                            ➊    
value_ready.store(true, std::memory_order_release); //                    ➋ ▲▲▲▲