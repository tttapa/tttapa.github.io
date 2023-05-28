#include <utility> // std::exchange

struct Node {
    Node *next = nullptr;
};

Node *reverse_linked_list(Node *fwd) {
    Node *rev = nullptr;
    while (fwd)
        rev = std::exchange(fwd, std::exchange(fwd->next, rev));
    return rev;
}
