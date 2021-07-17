// GPIO pin with the fader knob and pull-up resistor:
constexpr uint8_t touch_pin = 8;
// Frequency at which the Timer2 interrupt fires:
constexpr float interrupt_freq = 31'250;
// Interrupts per control loop period:
constexpr uint8_t interrupt_divisor = 30;
// Minimum RC-time to consider fader knob touched:
constexpr float touch_rc_time_threshold = 160e-6; // seconds
// Same threshold, but as a number of interrupts rather than seconds:
constexpr uint8_t touch_sense_thres = interrupt_freq * touch_rc_time_threshold;
static_assert(touch_sense_thres < interrupt_divisor, "RC-time too long");

volatile bool touched = false; // Whether the knob is touched or not

// Fires at a constant rate of 31,250 Hz:
ISR(TIMER2_OVF_vect) {
    static uint8_t counter = 0;

    if (counter == 0) {
        pinMode(touch_pin, INPUT); // start charging
    } else if (counter == touch_sense_thres) {
        touched = digitalRead(touch_pin) == LOW;
        pinMode(touch_pin, OUTPUT); // start discharging
    }

    ++counter;
    if (counter == interrupt_divisor)
        counter = 0;
}