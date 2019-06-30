#pragma once

namespace ANSIColors {
constexpr const char *reset = "\x1b[0m";

constexpr const char *black   = "\x1b[30m";
constexpr const char *red     = "\x1b[31m";
constexpr const char *green   = "\x1b[32m";
constexpr const char *yellow  = "\x1b[33m";
constexpr const char *blue    = "\x1b[34m";
constexpr const char *magenta = "\x1b[35m";
constexpr const char *cyan    = "\x1b[36m";
constexpr const char *white   = "\x1b[37m";

constexpr const char *blackb   = "\x1b[30;1m";  ///< Black bold
constexpr const char *redb     = "\x1b[31;1m";  ///< Red bold
constexpr const char *greenb   = "\x1b[32;1m";  ///< Green bold
constexpr const char *yellowb  = "\x1b[33;1m";  ///< Yellow bold
constexpr const char *blueb    = "\x1b[34;1m";  ///< Blue bold
constexpr const char *magentab = "\x1b[35;1m";  ///< Magenta bold
constexpr const char *cyanb    = "\x1b[36;1m";  ///< Cyan bold
constexpr const char *whiteb   = "\x1b[37;1m";  ///< White bold

}  // namespace ANSIColors

#include <ostream>

class Color {
  private:
    std::ostream &os;
    const char *color;

  public:
    Color(std::ostream &os, const char *color) : os(os), color(color) {}
    ~Color() { os << ANSIColors::reset << std::flush; }
    template <class T>
    std::ostream &operator<<(T &&t) const {
        return os << color << t;
    }
};

class Green : public Color {
  public:
    Green(std::ostream &os) : Color(os, ANSIColors::green) {}
};

class Yellow : public Color {
  public:
    Yellow(std::ostream &os) : Color(os, ANSIColors::yellow) {}
};

class Red : public Color {
  public:
    Red(std::ostream &os) : Color(os, ANSIColors::red) {}
};