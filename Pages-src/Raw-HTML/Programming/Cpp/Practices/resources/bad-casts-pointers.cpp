int value = 42;
int *very_bad = (int *)value; // accidental int-to-pointer conversion

const char *message = "12345";
int bad             = (int)message; // accidental pointer-to-int conversion
int also_bad        = int(message); // idem
