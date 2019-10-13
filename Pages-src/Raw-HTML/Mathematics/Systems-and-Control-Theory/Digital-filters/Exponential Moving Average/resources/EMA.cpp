#include <stdint.h>

template <uint8_t K, class uint_t = uint16_t>
class EMA {
  public:
    uint_t operator()(uint_t x) {
        z += x;
        uint_t y = (z + (1 << (K - 1))) >> K;
        z -= y;
        return y;
    }

    static_assert(
        uint_t(0) < uint_t(-1),  // Check that `uint_t` is an unsigned type
        "Error: the uint_t type should be an unsigned integer, otherwise, "
        "the division using bit shifts is invalid.");

  private:
    uint_t z = 0;
};