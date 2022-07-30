#pragma once

#include <Eigen/Dense>
#include <algorithm>
#include <utility>

namespace poly {

template <class T = double>
using coef_t = Eigen::VectorX<T>;
using index_t = Eigen::Index;

template <class T, class BasisTag>
struct GenericPolynomial {
    GenericPolynomial() = default;
    GenericPolynomial(coef_t<T> coefficients)
        : coefficients({std::move(coefficients)}) {}
    explicit GenericPolynomial(index_t degree)
        : coefficients {coef_t<T>::Zeros(degree + 1)} {}
    explicit GenericPolynomial(std::initializer_list<T> coefficients)
        : coefficients {coefficients.size()} {
        std::copy(std::begin(coefficients), std::end(coefficients),
                  std::begin(this->coefficients));
    }
    coef_t<T> coefficients;
};

struct MonomialBasis_t {
} inline constexpr MonomialBasis;
struct ChebyshevBasis_t {
} inline constexpr ChebyshevBasis;

template <class T = double>
using Polynomial = GenericPolynomial<T, MonomialBasis_t>;
template <class T = double>
using ChebyshevPolynomial = GenericPolynomial<T, ChebyshevBasis_t>;

} // namespace poly