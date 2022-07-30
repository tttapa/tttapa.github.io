#include <iostream>
#include <poly_eval.hpp>

int main() {
    // Create the polynomial p(x) = 1 - 2x + 3x² - 4x³ + 5x⁴
    poly::Polynomial<> p {1, -2, 3, -4, 5};
    // Evaluate the polynomial at x = 3
    std::cout << evaluate(p, 3.) << std::endl;
}