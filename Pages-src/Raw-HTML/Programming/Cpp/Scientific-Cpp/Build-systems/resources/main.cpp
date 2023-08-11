#include <b.hpp>
#include <vector>

int main() {
    std::vector<std::string_view> people{"John", "Paul", "George", "Ringo"};
    greet_many(people);
}
