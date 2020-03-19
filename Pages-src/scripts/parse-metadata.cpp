#include <cstring>
#include <parse-metadata.hpp>

#include <iostream>

class matcher {
  public:
    matcher(const char *str)
        : str(str), cur(str), end(str + std::strlen(str)) {}

    void reset() { cur = str; }

    bool operator()(char c) {
        if (c == *cur) {
            ++cur;
        } else {
            reset();
            return false;
        }
        if (cur == end) {
            reset();
            return true;
        }
        return false;
    }

  private:
    const char *const str;
    const char *cur;
    const char *const end;
};

class escaper {
  public:
    escaper(char esc = '\\') : esc(esc) {}

    explicit operator bool() const { return escape; }

    void operator()(char c) {
        if (c == esc && !escape) {
            escape = true;
        } else {
            escape = false;
        }
    }

    bool is_normal_char(char c) const { return c != esc || escape; }

  private:
    char esc;
    bool escape = false;
};

std::map<std::string, std::string> parse_metadata(const char *contents,
                                                  const char *path) {
    enum {
        normal = 0,
        comment = 1,
        key = 2,
        value = 4,
    } state = normal;

    matcher start_comment_matcher = "<!--";
    matcher end_comment_matcher = "-->";
    escaper escape = '\\';

    std::string key_str = "";
    std::string val_str = "";

    std::map<std::string, std::string> metadata;
    size_t lineno = 1, colno = 0;

    const char *c = contents;
    while (*c) {
        if (*c == '\n') {
            ++lineno;
            colno = 0;
        }
        if (*c == '\r') {
            colno = 0;
        }
        if ((*c & 0xC0) != 0x80) {
            ++colno;
        }

        if (state == normal) {
            if (start_comment_matcher(*c)) {
                state = comment;
            }
        } else if (state == comment) {
            if (*c == '@' && !escape) {
                state = key;
            }
            escape(*c);
        } else if (state == key) {
            if (end_comment_matcher(*c)) {
                throw std::runtime_error(
                    "Expected ':' before end of metadata at " +
                    std::string(path) + ":" + std::to_string(lineno) + ":" +
                    std::to_string(colno - 3));
            }
            if (*c == ':' && !escape) {
                state = value;
            } else if (escape.is_normal_char(*c)) {
                key_str += *c;
            }
            escape(*c);
        } else if (state == value) {
            if (end_comment_matcher(*c)) {
                if (!key_str.empty()) {
                    val_str.resize(val_str.size() - 2); // remove "-->"
                    metadata[std::move(key_str)] = std::move(val_str);
                }
                break;
            } else if (*c == '@' && !escape) {
                if (!key_str.empty()) {
                    metadata[std::move(key_str)] = std::move(val_str);
                }
                state = key;
            } else if (escape.is_normal_char(*c)) {
                val_str += *c;
            }
            escape(*c);
        }

        c++;
    }
    return metadata;
}
