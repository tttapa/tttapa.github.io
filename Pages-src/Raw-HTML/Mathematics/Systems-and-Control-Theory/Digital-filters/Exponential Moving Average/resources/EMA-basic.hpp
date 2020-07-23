#pragma once
#include <cstdint>     // uint8_t, uint16_t
#include <type_traits> // std::is_unsigned

/// The first Exponential Moving Average implementation for unsigned integers.
///
/// @note   An improved implementation is presented further down the page.
template <uint8_t K, class uint_t = uint16_t>
class EMA {
  public:
    /// Update the filter with the given input and return the filtered output.
    uint_t operator()(uint_t input) {
        state += input;
        uint_t output = (state + half) >> K;
        state -= output;
        return output;
    }

    static_assert(std::is_unsigned<uint_t>::value,
                  "The `uint_t` type should be an unsigned integer, "
                  "otherwise, the division using bit shifts is invalid.");

    /// Fixed point representation of one half, used for rounding.
    constexpr static uint_t half = 1 << (K - 1);

  private:
    uint_t state = 0;
};