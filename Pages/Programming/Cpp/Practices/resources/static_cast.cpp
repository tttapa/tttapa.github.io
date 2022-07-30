struct Pineapple { /* ... */ };
class Bulldozer { /* ... */ };

Pineapple p;
Bulldozer *b = static_cast<Bulldozer *>(&p); // compile-time error (as it should)