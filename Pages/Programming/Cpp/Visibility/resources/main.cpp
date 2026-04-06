#include <cstdio>

void func() { std::puts("func"); }

static void static_func() { std::puts("static_func"); }

namespace {
void anonymous_func() { std::puts("anonymous_func"); }
} // namespace

inline void inline_func() { std::puts("inline_func"); }

template <class T>
void template_func() {
    std::puts("template_func<...>");
}

template <class T>
inline void inline_template_func() {
    std::puts("inline_template_func<...>");
}

template <class T>
struct Class {
    void func() { std::puts("Class<...>::func"); }
    static void static_func() { std::puts("Class<...>::static_func"); }
    void out_of_line_func();
};

template <class T>
void Class<T>::out_of_line_func() {
    std::puts("Class<...>::out_of_line_func");
}

struct NoInst;

struct InstDefault;
template struct [[gnu::visibility("default")]] Class<InstDefault>;

template <class T>
struct [[gnu::visibility("default")]] DefaultClass {
    void func() { std::puts("Class<...>::func"); }
    static void static_func() { std::puts("Class<...>::static_func"); }
    void out_of_line_func();
};

template <class T>
void DefaultClass<T>::out_of_line_func() {
    std::puts("Class<...>::out_of_line_func");
}

struct Inst;
template struct DefaultClass<Inst>;

struct InstProtected;
template struct [[gnu::visibility("protected")]] DefaultClass<InstProtected>;

[[gnu::visibility("default")]] void default_func() {
    std::puts("default_func");
}

[[gnu::visibility("protected")]] void protected_func() {
    std::puts("protected_func");
}

[[gnu::visibility("hidden")]] void hidden_func() { std::puts("hidden_func"); }

int main() {
    func();
    static_func();
    anonymous_func();
    inline_func();
    template_func<int>();
    inline_template_func<int>();
    Class<NoInst> obj;
    obj.func();
    obj.static_func();
    obj.out_of_line_func();
    Class<InstDefault> inst_default_obj;
    inst_default_obj.func();
    inst_default_obj.static_func();
    inst_default_obj.out_of_line_func();
    DefaultClass<NoInst> default_obj;
    default_obj.func();
    default_obj.static_func();
    default_obj.out_of_line_func();
    DefaultClass<Inst> default_inst_obj;
    default_inst_obj.func();
    default_inst_obj.static_func();
    default_inst_obj.out_of_line_func();
    DefaultClass<InstProtected> default_inst_protected_obj;
    default_inst_protected_obj.func();
    default_inst_protected_obj.static_func();
    default_inst_protected_obj.out_of_line_func();
    default_func();
    protected_func();
    hidden_func();
}
