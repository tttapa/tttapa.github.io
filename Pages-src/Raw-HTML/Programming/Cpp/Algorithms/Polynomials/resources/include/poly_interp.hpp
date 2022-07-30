#pragma once

#include <Eigen/LU>
#include <poly.hpp>
#include <vector>

namespace poly {

template <class T = double>
using vector_t = Eigen::VectorX<T>;

namespace detail {

template <class T, class F>
coef_t<T> interpolate(Eigen::Ref<const vector_t<T>> x,
                      Eigen::Ref<const vector_t<T>> y, F &&vanderfun) {
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
auto make_monomial_vandermonde_system(Eigen::Ref<const vector_t<T>> x,
                                      index_t degree) {
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
Polynomial<T> interpolate(Eigen::Ref<const vector_t<T>> x,
                          Eigen::Ref<const vector_t<T>> y, MonomialBasis_t) {
    auto coef =
        detail::interpolate(x, y, detail::make_monomial_vandermonde_system<T>);
    return {std::move(coef)};
}

namespace detail {

template <class T>
auto make_chebyshev_vandermonde_system(Eigen::Ref<const vector_t<T>> x,
                                       index_t degree) {
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
ChebyshevPolynomial<T> interpolate(Eigen::Ref<const vector_t<T>> x,
                                   Eigen::Ref<const vector_t<T>> y,
                                   ChebyshevBasis_t) {
    auto coef =
        detail::interpolate(x, y, detail::make_chebyshev_vandermonde_system<T>);
    return {std::move(coef)};
}

template <class T, class Basis>
GenericPolynomial<T, Basis> interpolate(const vector_t<T> &x,
                                        const vector_t<T> &y, Basis basis) {
    return interpolate(Eigen::Ref<const vector_t<T>>(x),
                       Eigen::Ref<const vector_t<T>>(y), basis);
}

template <class T, class Basis>
GenericPolynomial<T, Basis> interpolate(const std::vector<T> &x,
                                        const std::vector<T> &y, Basis basis) {
    return interpolate(Eigen::Ref<const vector_t<T>>(
                           Eigen::Map<const vector_t<T>>(x.data(), x.size())),
                       Eigen::Ref<const vector_t<T>>(
                           Eigen::Map<const vector_t<T>>(y.data(), y.size())),
                       basis);
}

} // namespace poly