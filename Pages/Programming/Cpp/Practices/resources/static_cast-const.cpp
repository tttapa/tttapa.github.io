const char *message = "12345";
char *little_better = static_cast<char *>(message); // compile-time error (as it should)