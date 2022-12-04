#pragma once

#include <Eigen/LU>
#include <poly.hpp>
#include <vector>

namespace poly {

namespace detail {

template <class T, class F>
coef_t<T> interpolate(vector_ref_t<T> x, vector_ref_t<T> y, F &&vanderfun) {
    assert(x.size() == y.size());
    assert(x.size() > 0);
    // Construct Vandermonde matrix
    auto V = vanderfun(x, x.size() - 1);
    // Scale the system
    const vector_t<T> scaling = V.colwise().norm().cwiseInverse();
    V *= scaling.asDiagonal();
    // Solve the system
    vector_t<T> solution = V.fullPivLu().solve(y);
    solution.transpose() *= scaling.asDiagonal();
    return solution;
}

template <class T>
auto make_monomial_vandermonde_system(vector_ref_t<T> x, index_t degree) {
    assert(degree >= 0);
    const index_t N = x.size();
    Eigen::MatrixXd V(N, degree + 1);
    V.col(0) = Eigen::VectorXd::Ones(N);
    for (Eigen::Index i = 0; i < degree; ++i)
        V.col(i + 1) = V.col(i).cwiseProduct(x);
    return V;
}

} // namespace detail

template <class T>
Polynomial<T> interpolate(vector_ref_t<T> x, vector_ref_t<T> y,
                          MonomialBasis_t) {
    auto *vanderfun = detail::make_monomial_vandermonde_system<T>;
    auto coef = detail::interpolate(x, y, vanderfun);
    return {std::move(coef)};
}

namespace detail {

template <class T>
auto make_chebyshev_vandermonde_system(vector_ref_t<T> x, index_t degree) {
    assert(degree >= 0);
    const index_t N = x.size();
    Eigen::MatrixXd V(N, degree + 1);
    V.col(0) = Eigen::VectorXd::Ones(N);
    if (degree >= 1) {
        V.col(1) = x;
        for (Eigen::Index i = 0; i < degree - 1; ++i)
            V.col(i + 2) = 2 * V.col(i + 1).cwiseProduct(x) - V.col(i);
    }
    return V;
}

} // namespace detail

template <class T>
ChebyshevPolynomial<T> interpolate(vector_ref_t<T> x, vector_ref_t<T> y,
                                   ChebyshevBasis_t) {
    auto *vanderfun = detail::make_chebyshev_vandermonde_system<T>;
    auto coef = detail::interpolate(x, y, vanderfun);
    return {std::move(coef)};
}

template <class T, class Basis>
GenericPolynomial<T, Basis> interpolate(const vector_t<T> &x,
                                        const vector_t<T> &y, Basis basis) {
    return interpolate(vector_ref_t<T> {x}, vector_ref_t<T> {y}, basis);
}

template <class T, class Basis>
GenericPolynomial<T, Basis> interpolate(const std::vector<T> &x,
                                        const std::vector<T> &y, Basis basis) {
    return interpolate(detail::vector_map_ref(x), detail::vector_map_ref(y),
                       basis);
}

} // namespace poly