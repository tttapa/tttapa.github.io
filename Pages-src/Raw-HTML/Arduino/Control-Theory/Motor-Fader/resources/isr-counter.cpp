constexpr uint8_t num_faders = 3;
constexpr uint8_t interrupt_divisor = 30;
constexpr uint8_t adc_start_count = interrupt_divisor / num_faders;

// Fires at a constant rate of 31,250 Hz:
ISR(TIMER2_OVF_vect) {
    static uint8_t counter = 0;

    for (uint8_t fader = 0; fader < num_faders; ++fader) {
        if (counter == fader * adc_start_count) {
            startADCConversion(fader);
            break;
        }
    }

    ++counter;
    if (counter == interrupt_divisor)
        counter = 0;
}