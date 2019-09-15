#include <stdint.h>

template <uint8_t K, class uint_t>
class EMA {
  public:
    uint_t filter(uint_t x) {
        z += x;
        uint_t y = (z + (1 << (K - 1))) >> K;
        z -= y;
        return y;
    }

  private:
    uint_t z = 0;
};