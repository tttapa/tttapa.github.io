#pragma once

#include <Eigen/Dense>
#include <algorithm>
#include <utility>
#include <vector>

namespace poly {

template <class T = double>
using vector_t = Eigen::VectorX<T>;
template <class T = double>
using vector_ref_t = Eigen::Ref<const vector_t<T>>;
template <class T = double>
using vector_mut_ref_t = Eigen::Ref<vector_t<T>>;
template <class T = double>
using coef_t = vector_t<T>;
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

namespace detail {
template <class Container>
vector_ref_t<typename Container::value_type>
vector_map_ref(const Container &x) {
    return Eigen::Map<const vector_t<typename Container::value_type>>(x.data(),
                                                                      x.size());
}
template <class Container>
vector_mut_ref_t<typename Container::value_type> vector_map_ref(Container &x) {
    return Eigen::Map<vector_t<typename Container::value_type>>(x.data(),
                                                                x.size());
}
} // namespace detail

} // namespace poly