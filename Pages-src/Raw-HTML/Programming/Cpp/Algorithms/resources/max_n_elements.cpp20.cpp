#include <algorithm> // ranges::partial_sort_copy
#include <ranges>    // views::iota, ranges::forward_range, ranges::borrowed_iterator_t
#include <vector>    // vector

/**
 * @brief   Return a vector of iterators to the n largest elements of the given
 *          range.
 * 
 * @tparam  R 
 *          The type of range.
 * @param   range 
 *          The input range to find the largest elements in.
 * @param   n 
 *          The number of largest elements to return.
 * 
 * @return  Vector containing iterators to the n largest elements of the range.
 */
template <std::ranges::forward_range R>
constexpr std::vector<std::ranges::borrowed_iterator_t<R>>
max_n_elements(R &&range, size_t n) {
    // The iterator type of the input range
    using iter_t = std::ranges::borrowed_iterator_t<R>;
    // The range of iterators over the input range
    auto iterators = std::views::iota(std::ranges::begin(range), 
                                      std::ranges::end(range));
    // Vector of iterators to the largest n elements
    std::vector<iter_t> result(n);
    // Lambda function to compare two iterators: dereference them and compare 
    // their values
    auto compare = [](iter_t it_a, iter_t it_b) { return *it_a > *it_b; };
    // Sort the largest n elements of the input range, and store iterators to 
    // these elements to the result vector
    std::ranges::partial_sort_copy(iterators, result, compare);
    return result;
}

#include <iostream>

int main() {
    std::vector<int> v = {10, 12, 8, -5, 8, 3, -2, 1, 9, 12};
    size_t n = 4;
    auto max_elems = max_n_elements(v, n);
    std::cout << "Largest elements:" << std::endl;
    for (auto it : max_elems) {
        auto idx = it - v.begin();
        std::cout << "   [" << idx << "]:\t" << *it << std::endl;
    }
}