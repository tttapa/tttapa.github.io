#include <iostream>
#include <poly_eval.hpp>
#include <poly_interp.hpp>

int main() {
    std::cout.precision(17);
    // Evaluate some points on this polynomial
    poly::Polynomial<> p {1, -2, 3, -4, 5};
    poly::vector_t<> x = poly::vector_t<>::LinSpaced(5, -1, 1);
    poly::vector_t<> y = x.unaryExpr([p](double x) { return evaluate(p, x); });
    // Interpolate the data
    poly::Polynomial<> p_interp = interpolate(x, y, poly::MonomialBasis);
    std::cout << p_interp.coefficients.transpose() << std::endl;

    // Now do the same with std::vectors
    std::vector<double> vx {x.begin(), x.end()};
    std::vector<double> vy {y.begin(), y.end()};
    p_interp = interpolate(vx, vy, poly::MonomialBasis);
    std::cout << p_interp.coefficients.transpose() << std::endl;

    // Fit a Chebyshev polynomial through the same points
    poly::ChebyshevPolynomial<> p_cheb =
        interpolate(x, y, poly::ChebyshevBasis);
    std::cout << p_cheb.coefficients.transpose() << std::endl;
    // Evaluate the polynomial again to verify
    poly::vector_t<> yc =
        x.unaryExpr([p_cheb](double x) { return evaluate(p_cheb, x); });
    std::cout << y.transpose() << std::endl;
    std::cout << yc.transpose() << std::endl;
}