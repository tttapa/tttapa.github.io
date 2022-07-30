const char *message = "12345";
char *very_bad = (char *)message; // casts away const

volatile uint8_t buffer[8];
uint8_t *also_very_bad = (uint8_t *)buffer; // casts away volatile