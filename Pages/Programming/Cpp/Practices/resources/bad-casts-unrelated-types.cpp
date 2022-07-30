struct Pineapple { /* ... */ };
class Bulldozer { /* ... */ };

Pineapple p;
Bulldozer *b = (Bulldozer *)&p; // b points to a pineapple, not a bulldozer