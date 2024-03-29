#include <algorithm>
#include <array>
#include <cassert>
#include <cctype>
#include <chrono>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <future>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <optional>
#include <regex>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <pybind11/embed.h>
#include <pybind11/stl.h>

#include "ANSIColors.hpp"
#include "parse-metadata.hpp"
#include "trim.hpp"

namespace fs = std::filesystem;
namespace py = pybind11;
using std::cerr;
using std::cout;
using std::endl;
using std::ifstream;
using std::optional;
using std::regex;
using std::regex_replace;
using std::regex_search;
using std::string;
using std::stringstream;
using std::vector;
using std::filesystem::path;

using string_map = std::map<string, string>;
using file_time_t = std::filesystem::file_time_type;

template <class... Ts>
struct overloaded : Ts... {
    using Ts::operator()...;
};

class PagesParser {
  public:
    struct Page {
        bool is_folder = false;
        string_map metadata;
        string html;
        unsigned int lineno; ///< line number where <html> starts
        file_time_t modified;
        file_time_t depmodified;
        path abs_source_path;
        path rel_path;
        std::optional<int> sectionNumber = std::nullopt;
        const Page *previous = nullptr, *next = nullptr;
        const Page *parent = nullptr;

        std::optional<int> getStartSectionNumber() const {
            if (auto it = metadata.find("section-number");
                it != metadata.end()) {
                return std::stoi(it->second);
            }
            return {};
        }

        int getSequenceNumber() const {
            if (auto seq_str_it = metadata.find("sequence");
                seq_str_it != metadata.end()) {
                try {
                    return std::stoi(seq_str_it->second);
                } catch (std::exception &) {
                    Yellow(cerr) << "Warning: invalid sequence number for "
                                 << abs_source_path << endl;
                    return std::numeric_limits<int>::max();
                }
            } else {
                return std::numeric_limits<int>::max();
            }
        }

        string getTitle() const {
            if (auto title_it = metadata.find("title");
                title_it != metadata.end()) {
                return title_it->second;
            } else {
                Red(cerr) << "Warning: no valid title for " << abs_source_path
                          << endl;
                return abs_source_path.stem();
            }
        }

        string getFullTitle() const {
            if (auto pfx = getSectionNumbers(); !pfx.empty())
                return pfx + ' ' + getTitle();
            return getTitle();
        }

        string getSectionNumbers() const {
            if (!sectionNumber)
                return "";
            auto thisSectionNumber = std::to_string(*sectionNumber) + '.';
            if (!parent)
                return thisSectionNumber;
            return parent->getSectionNumbers() + thisSectionNumber;
        }

        string getDescription() const {
            if (auto descr_it = metadata.find("description");
                descr_it != metadata.end()) {
                return descr_it->second;
            } else {
                Red(cerr) << "Warning: no valid description for "
                          << abs_source_path << endl;
                return "";
            }
        }

        string getArticleClass() const {
            if (auto class_it = metadata.find("article-class");
                class_it != metadata.end()) {
                auto cls = class_it->second;
                auto attrs = " class=\"" + cls + "\"";
                if (cls == "book-chapter") {
                    if (!sectionNumber)
                        throw std::runtime_error(
                            "Missing section number for book-chapter. Add "
                            "@section-number: 1 to index.html metadata");
                    attrs += " style=\"counter-reset: book-chapter " +
                             std::to_string(*sectionNumber) +
                             " book-section2 0 book-section3 0;\"";
                } else if (cls == "book-section") {
                    if (!parent)
                        throw std::runtime_error(
                            "Missing parent for book-section");
                    if (!sectionNumber)
                        throw std::runtime_error(
                            "Missing section number for book-section. Add "
                            "@section-number: 1 to index.html metadata");
                    if (!parent->sectionNumber)
                        throw std::runtime_error(
                            "Missing section number for parent of "
                            "book-section. Add "
                            "@section-number: 1 to parent index.html metadata");
                    attrs += " style=\"counter-reset: book-chapter " +
                             std::to_string(*parent->sectionNumber) +
                             " book-section " + std::to_string(*sectionNumber) +
                             " book-section2 0 book-section3 0;\"";
                }
                return attrs;
            } else {
                return "";
            }
        }
    };

    struct PageDirectory : public Page {
        vector<std::unique_ptr<std::variant<Page, PageDirectory>>>
            pages_and_subdirs;
        vector<path> resources;
        PageDirectory() { is_folder = true; }
    };

    enum Task {
        ClientSideLaTeX,
        ServerSideLaTeX,
        ServerSideLaTeXPDF,
    };

  public:
    PagesParser(path source_dir, path output_dir, path template_dir)
        : source_dir(source_dir), output_dir(output_dir),
          template_dir(template_dir) {}

    void load() {
        init();
        load_page_directory(source_dir, root);
    }

    Task task;

    void exportAll(Task task = ClientSideLaTeX, unsigned int num_threads = 0) {
        py::scoped_interpreter interpreter{};
        path file = __FILE__;
        path folder = file.parent_path();
        py::module sys = py::module::import("sys");
        sys.attr("path").cast<py::list>().append(folder.string());
        py::globals()["HTMLFormatter"] = py::module::import("HTMLFormatter");
        this->task = task;
        bool exportLaTeX =
            task == ServerSideLaTeX || task == ServerSideLaTeXPDF;
        if (exportLaTeX && num_threads <= 0)
            num_threads = 2 * std::thread::hardware_concurrency();
        if (exportLaTeX) {
            assert(num_threads > 0);
            this->mjpage_futures.resize(num_threads);
        }
        if (task == ServerSideLaTeXPDF)
            startHTTPandChromeServers();
        exportDirectory(root);
        if (exportLaTeX)
            wait_all_mjpage();
        // cout << "LaTeX compilation done" << endl;
        if (task == ServerSideLaTeXPDF)
            exportPDFDirectory(root);
    }

  private:
    const int dev_port = 9222;
    const int http_port = 5741;

    const path tmp_dir = "/tmp/Pages";

    vector<std::future<const Page &>> mjpage_futures = {};

    void startHTTPandChromeServers() {
        string c = "cd \"" + output_dir.parent_path().string() +
                   "\" && python3 -m http.server " + std::to_string(http_port) +
                   " --bind 127.0.0.1 &";
        cout << c << endl;
        if (system(c.c_str()) != 0)
            throw std::runtime_error("Command '" + c + "' failed.");
        c = "{ chromium --headless --disable-gpu "
            "--run-all-compositor-stages-before-draw --remote-debugging-port=" +
            std::to_string(dev_port) + " 2>&1; } &";
        cout << c << endl;
        if (system(c.c_str()) != 0)
            throw std::runtime_error("Command '" + c + "' failed.");
        BlueB(cout) << "Chrome started." << endl;
    }

    void handle_finished_mjpage(const Page &page) {
        std::ifstream f(output_dir / page.rel_path);
        string line;
        if (std::getline(f, line) && line != "<!DOCTYPE HTML>")
            throw std::runtime_error("MathJax compilation failed for " +
                                     page.getTitle() + " (" +
                                     page.abs_source_path.string() + ")");
        Green(cout) << "Page `" << page.getTitle() << "` finished" << endl;
    }

    void export_mjpage(const Page &page, const string &out) {
        using namespace std::chrono_literals;
        fs::create_directories(tmp_dir / page.rel_path.parent_path());
        fs::create_directories(output_dir / page.rel_path.parent_path());
        std::ofstream outfile(tmp_dir / page.rel_path);
        outfile << out;
        outfile.close();
        path scripts_dir = source_dir.parent_path() / "scripts";
        string command = scripts_dir / "mathjax-compile-chtml.js";
        command += " \"";
        command += tmp_dir / page.rel_path;
        command += "\" > \"";
        command += output_dir / page.rel_path;
        command += "\"";

        bool launched = false;
        const Page *finishedPage = nullptr;
        while (!launched) {
            for (auto &fut : mjpage_futures) {
                if (fut.valid() == false || // uninitialized
                    fut.wait_for(10ms) == std::future_status::ready) {
                    finishedPage = fut.valid() ? &(fut.get()) : nullptr;
                    Blue(cout) << "Started compiling Page `" << page.getTitle()
                               << "`" << endl;
                    auto launch = [command, &page]() -> const Page & {
                        if (system(command.c_str()) != 0) {
                            throw std::runtime_error("Command '" + command +
                                                     "' failed.");
                        } // TODO
                        return page;
                    };
                    fut = std::async(std::launch::async, launch);
                    launched = true;
                    break; // for
                }
            }
        }
        if (finishedPage)
            handle_finished_mjpage(*finishedPage);
    }

    void wait_all_mjpage() {
        using namespace std::chrono_literals;
        bool allReady = false;
        while (!allReady) {
            allReady = true;
            for (auto &fut : mjpage_futures) {
                if (fut.valid() == false || // uninitialized
                    fut.wait_for(1ms) == std::future_status::ready) {
                    if (fut.valid())
                        handle_finished_mjpage(fut.get());
                    fut = {};

                } else {
                    allReady = false;
                }
            }
        }
    }

    void exportPage(const Page &page, const string &template_content) {
        bool exportLaTeX = task == ServerSideLaTeX || //
                           task == ServerSideLaTeXPDF;
        string out = createPage(page, template_content, exportLaTeX);
        bool hasLaTeX = false;
        hasLaTeX = hasLaTeX || out.find("\\(") != string::npos;
        hasLaTeX = hasLaTeX || out.find("$$") != string::npos;
        hasLaTeX = hasLaTeX || out.find("\\[") != string::npos;
        if (exportLaTeX && hasLaTeX) {
            export_mjpage(page, out);
        } else {
            Green(cout) << "Exporting page `" << page.getTitle() << "`" << endl;
            std::ofstream outfile(output_dir / page.rel_path);
            outfile << out;
        }
    }

    /**
     * @brief   Export a regular page.
     */
    void exportPage(const Page &page) { exportPage(page, page_template); }

    /**
     * @brief   Export the index page of a directory.
     */
    void exportPage(const PageDirectory &page) {
        string out = index_template;
        replace(out, ":index:", generateIndex(page));
        exportPage(page, out);
    }

    string createPage(const Page &page, string pageTemplate, bool mathjax) {
        string out = pageTemplate;
        replace(out, ":mathjax:",
                mathjax ? "<!-- No MathJax -->" : mathjax_template);
        auto title = page.getFullTitle();
        replace(out, ":title:", title);
        replace(out, ":nav:", generateNavigation(page));
        replace(out, ":filenamepdf:", page.rel_path.stem().string() + ".pdf");
        string html = page.html;
        replace(out, ":html:",
                formatHTML(page.html, page.abs_source_path, page.lineno,
                           output_dir / page.rel_path, page.metadata));
        auto shownextupprevpage_it = page.metadata.find("shownextupprevpage");
        bool showNextUpPrev = shownextupprevpage_it != page.metadata.end() &&
                              isTruthyString(shownextupprevpage_it->second);
        replace(out, ":nextupprev:",
                showNextUpPrev ? generateNextUpPrevNav(page) : "");
        replace(out, ":mdate:", formatFileTime(page.modified));
        replace(out, ":article-class:", page.getArticleClass());
        for (const auto &[key, value] : page.metadata)
            replace(out, ":" + key + ":", value);
        return out;
    }

    void exportDirectory(const PageDirectory &dir) {
        try {
            // Create the folder structure in the output directory
            fs::create_directories(output_dir / dir.rel_path.parent_path());
            // Export the index page of the current directory
            exportPage(dir);
            // Export all other pages in this directory
            auto visitor = overloaded{
                [this](const PageDirectory &dir) { exportDirectory(dir); },
                [this](const Page &page) { exportPage(page); },
            };
            for (auto &page_or_subdir : dir.pages_and_subdirs)
                std::visit(visitor, *page_or_subdir);
            // Copy all resource folders
            for (auto &dir : dir.resources)
                fs::copy(source_dir / dir, output_dir / dir,
                         fs::copy_options::overwrite_existing |
                             fs::copy_options::recursive);
        } catch (std::exception &e) {
            Red(cerr) << "Error exporting directory "
                      << dir.abs_source_path.parent_path() << ": " << e.what()
                      << endl;
            throw;
        }
    }

    void exportPDFPage(const Page &page) {
        path pdf_file = output_dir / page.rel_path;
        pdf_file.replace_extension(".pdf");
        if (fs::exists(pdf_file) &&
            page.modified <= fs::last_write_time(pdf_file) &&
            page.depmodified <= fs::last_write_time(pdf_file))
            return;
        path file = __FILE__;
        path folder = file.parent_path();
        string command = "cd \"";
        command += folder;
        command += "\" && ";
        command += "./print-to-pdf-puppeteer.js \"";
        command += std::to_string(dev_port);
        command += "\" \"";
        command += "http://localhost:";
        command += std::to_string(http_port);
        command += "/";
        command += output_dir.filename();
        command += "/";
        command += page.rel_path;
        command += "\" \"";
        command += pdf_file;
        command += "\"";
        if (int status = system(command.c_str()); status != 0) {
            Red(cerr) << "print-to-pdf-puppeteer.js for `" << page.getTitle()
                      << "` failed with exit status " << status << endl;
        }
    }

    void exportPDFDirectory(const PageDirectory &dir) {
        // Export the index page of the current directory
        exportPDFPage(dir);
        // Export all other pages in this directory and subdirectories
        auto visitor = overloaded{
            [this](const PageDirectory &dir) { exportPDFDirectory(dir); },
            [this](const Page &page) { exportPDFPage(page); },
        };
        for (auto &page_or_subdir : dir.pages_and_subdirs)
            std::visit(visitor, *page_or_subdir);
    }

    static bool isTruthyString(string str) {
        const static string true_str[]{"1", "true", "yes", "y", "t"};
        const static string false_str[]{"0", "false", "no", "n", "f"};
        auto to_lower = [](char c) -> char { return std::tolower(c); };
        std::ranges::transform(str, str.begin(), to_lower);
        if (std::ranges::find(true_str, str) != std::end(true_str))
            return true;
        else if (std::ranges::find(false_str, str) != std::end(false_str))
            return false;
        else
            throw std::runtime_error("String should have truth value (e.g. "
                                     "\"true\" or \"false\"), got \"" +
                                     str + "\" instead.");
    }

    static bool isPageToList(const Page &page) {
        string filename = page.rel_path.filename();
        if (filename[0] == '.')
            return false;
        else if (auto hidden_str_it = page.metadata.find("hidden");
                 hidden_str_it != page.metadata.end())
            return !isTruthyString(hidden_str_it->second);
        else
            return true;
    }

    static bool isDirectoryToList(const PageDirectory &dir) {
        string dirname = dir.rel_path.parent_path().filename();
        if (dirname[0] == '.')
            return false;
        else if (auto hidden_str_it = dir.metadata.find("hidden");
                 hidden_str_it != dir.metadata.end())
            return !isTruthyString(hidden_str_it->second);
        else
            return true;
    }

    static bool isParentOf(const Page &entry, const Page &parent) {
        for (auto e = &entry; e != nullptr; e = e->parent)
            if (e == &parent)
                return true;
        return false;
    }

    string generateNavigation(const Page &page) {
        return generateNavigation(page, root);
    }

    string generateNavigation(const Page &page, const PageDirectory &root,
                              unsigned int level = 0) {
        string indentation_ul(4 * level, ' ');
        string indentation_li(4 * level + 4, ' ');

        string result = indentation_ul;
        result += "<ul>\n";
        auto gen_subdir = [&](const PageDirectory &entry) {
            bool open_entry = page.rel_path == entry.rel_path;
            string rel =
                fs::relative(page.rel_path, entry.rel_path.parent_path());
            bool expanded = rel.substr(0, 2) != "..";
            bool hidden = !isDirectoryToList(entry);
            if (hidden && !(open_entry || expanded))
                return;
            result += indentation_li;
            result += "<li";
            if (expanded)
                result += " class=\"expanded\"";
            result += ">";
            result += "<span class=\"dtriangle\" "
                      "onclick=\"this.parentElement.classList.toggle('"
                      "expanded');\">"
                      "</span>";
            result += "<a class=\"";
            if (hidden)
                result += "hiddenEntry ";
            if (open_entry)
                result += "openEntry ";
            result += "\" href=\"";
            result += fs::relative(entry.rel_path, page.rel_path.parent_path());
            result += "\">";
            result += entry.getFullTitle();
            result += "</a>\n";
            result += generateNavigation(page, entry, level + 1);
            result += indentation_li;
            result += "</li>\n";
        };
        auto gen_page = [&](const Page &entry) {
            string rel = fs::relative(page.rel_path, entry.rel_path);
            bool open_entry = rel == ".";
            bool hidden = !isPageToList(entry);
            if (hidden && !open_entry)
                return;
            result += indentation_li;
            result += "<li><span class=\"ftriangle\"></span>";
            result += "<a class=\"";
            if (hidden)
                result += "hiddenEntry ";
            if (open_entry)
                result += "openEntry ";
            result += "\" href=\"";
            result += fs::relative(entry.rel_path, page.rel_path.parent_path());
            result += "\">";
            result += entry.getFullTitle();
            result += "</a></li>\n";
        };
        auto visitor = overloaded{gen_subdir, gen_page};
        for (const auto &entry : root.pages_and_subdirs)
            std::visit(visitor, *entry);
        result += indentation_ul;
        result += "</ul>\n";
        return result;
    }

    string generateNextUpPrevNav(const Page &page) {
        string res = "";
        res += R"(<div class="prevpage">)";
        const auto &base_path = page.rel_path.parent_path();
        if (page.previous) {
            res += R"(<a href=")";
            res += fs::relative(page.previous->rel_path, base_path);
            res += R"(" title=")";
            res += page.previous->getFullTitle();
            res += R"("><i class="material-icons")"
                   R"( style="vertical-align: middle; text-decoration: none">)"
                   R"(chevron_left </i>Previous )";
            res += page.previous->is_folder ? "Chapter" : "Page";
            res += R"(</a>)";
        }
        res += R"(</div>)";
        res += R"(<div class="uppage">)";
        if (true) {
            res += R"(<a href=")";
            if (page.parent)
                res += fs::relative(page.parent->rel_path, base_path);
            else
                res += "index.html";
            res += R"(" title=")";
            res += page.parent ? page.parent->getFullTitle() : "Up";
            res += page.is_folder ? R"(">Up</a>)" : R"(">Index</a>)";
        }
        res += R"(</div>)";
        res += R"(<div class="nextpage">)";
        if (page.next) {
            res += R"(<a href=")";
            res += fs::relative(page.next->rel_path, base_path);
            res += R"(" title=")";
            res += page.next->getFullTitle();
            res += R"(">Next )";
            res += page.next->is_folder ? "Chapter" : "Page";
            res += R"(<i class="material-icons")"
                   R"( style="vertical-align: middle; text-decoration: none">)"
                   R"( chevron_right</i></a>)";
        }
        res += R"(</div>)";
        return res;
    }

    string generateIndexItem(const Page &page, const path &root) {
        string item = page.is_folder ? index_item_folder_template //
                                     : index_item_template;
        replace(item, ":title:", page.getFullTitle());
        replace(item, ":link:", fs::relative(page.rel_path, root));
        replace(item, ":description:", page.getDescription());
        return item;
    }

    string generateIndex(const PageDirectory &dir) {
        string result;
        auto gen_subdir = [&](const PageDirectory &entry) {
            if (!isDirectoryToList(entry))
                return;
            result += generateIndexItem(entry, dir.rel_path.parent_path());
        };
        auto gen_page = [&](const Page &entry) {
            if (!isPageToList(entry))
                return;
            result += generateIndexItem(entry, dir.rel_path.parent_path());
        };
        auto visitor = overloaded{gen_subdir, gen_page};
        for (const auto &entry : dir.pages_and_subdirs)
            std::visit(visitor, *entry);
        return result;
    }

  private:
#pragma region HTML formatter...................................................

    string formatHTML(const string &html, const fs::path &path,
                      unsigned int lineno, const fs::path &outpath,
                      const string_map &metadata) {
        auto formatHTML = py::globals()["HTMLFormatter"].attr("formatHTML");
        return formatHTML(html, path.string(), lineno, outpath.string(),
                          metadata)
            .cast<string>();
    }

#pragma endregion
#pragma region String utilities.................................................

    static string get_first_comment(const string &content) {
        regex comment_regex("<!--([^]*?)-->");
        std::smatch comment_match;
        if (!regex_search(content, comment_match, comment_regex) ||
            comment_match.size() != 2) {
            return "";
        }
        return convert_line_endings(comment_match[1]);
    }

    static string remove_double_spaces(const string &s) {
        regex re(" +");
        return regex_replace(s, re, " ");
    }

    static string remove_newlines(const string &s) {
        regex re("[\\r\\n]+");
        return regex_replace(s, re, " ");
    }

    static string convert_line_endings(const string &s) {
        regex re("\\r\\n");
        return regex_replace(s, re, "\n");
    }

    static bool replace(string &str, const string &from, const string &to) {
        bool ret = false;
        size_t start = str.find(from);
        while (start != string::npos) {
            ret = true;
            str.replace(start, from.length(), to);
            start = str.find(from, start + from.length());
        }
        return ret;
    }

    static string formatFileTime(file_time_t ft) {
        std::stringstream buffer;
        std::time_t tt = ft.time_since_epoch().count() / 1'000'000'000 +
                         6'437'664'000; // TODO: ugly non-portable hack
        std::tm *gmt = std::gmtime(&tt);
        buffer << std::put_time(gmt, "%A, %d %B %Y %H:%M");
        return buffer.str();
    }

#pragma endregion
#pragma region Loading source files.............................................

    void init() {
        load_template();
        mathjax_template = read_file(template_dir / "mathjax_template.html");
        page_template = read_file(template_dir / "template.html");
        index_template = read_file(template_dir / "template_index.html");
        index_item_template =
            read_file(template_dir / "template_index_item.html");
        index_item_folder_template =
            read_file(template_dir / "template_index_item_folder.html");
    }

    static string read_file(path filename) {
        ifstream file = filename;
        string contents;
        std::getline(file, contents, '\0');
        return contents;
    }

    void load_template() {
        metadata_template = read_file(template_dir / "template_meta.html");
        string comment = get_first_comment(metadata_template);
        if (comment.empty())
            Yellow(cerr) << "Warning: invalid metadata template ("
                         << (template_dir / "template_meta.html") << ")"
                         << endl;
        regex rgx("[\\r\\n]@(\\w+)");
        auto keys_begin =
            std::sregex_iterator(comment.begin(), comment.end(), rgx);
        auto keys_end = std::sregex_iterator();
        metadata_keys.resize(std::distance(keys_begin, keys_end));
        std::transform(keys_begin, keys_end, metadata_keys.begin(),
                       [](const std::smatch &m) -> string {
                           if (m.size() == 2)
                               return m[1];
                           return "";
                       });
    }

    static optional<string> read_metadata_value(const string &comment,
                                                const string &key) {
        std::string::size_type offset = key.size() + 3;
        auto first_match = comment.find("\n@" + key + ':');
        auto end_match = comment.find("\n@", first_match + offset);
        if (end_match == std::string::npos)
            end_match = comment.size();
        if (first_match != std::string::npos) {
            string raw = comment.substr(first_match + offset,
                                        end_match - first_match - offset);
            trim(raw);
            return remove_double_spaces(remove_newlines(raw));
        }
        return std::nullopt;
    }

    static std::tuple<string, unsigned int>
    read_html(const fs::directory_entry &file_entry, const string &content) {
        size_t offset = 6;
        size_t start = content.find("<html>");
        size_t end = content.rfind("</html>");
        if (start != string::npos && end != string::npos) {
            string html = content.substr(start + offset, end - start - offset);
            unsigned int lineno =
                std::count(content.begin(), content.begin() + start, '\n') + 1;
            return std::make_tuple(html, lineno);
        } else {
            Yellow(cerr) << "Warning: no valid html for " << file_entry << endl;
            return std::make_tuple<string>("", 0);
        }
    }

    string_map read_metadata(const fs::directory_entry &file_entry,
                             const string &content) {
        auto md = parse_metadata(content.c_str(), file_entry.path().c_str());
        // Trim the whitespace from the values
        for (auto &[k, v] : md) {
            trim(v);
            v = remove_double_spaces(remove_newlines(v));
        }
        // Check if all keys from the template are present
        for (const auto &key : metadata_keys) {
            if (md.find(key) == md.end()) {
                Yellow(cerr) << "Warning: missing value for key `" << key
                             << "` for " << file_entry << endl;
            }
        }
        return md;
    }

    file_time_t get_dep_modified(const fs::path &rpath) {
        std::ifstream file(output_dir / rpath.parent_path() /
                           (rpath.stem().string() + ".dep"));
        file_time_t time = file_time_t::min();
        std::string depfilename;
        while (std::getline(file, depfilename))
            try {
                auto deptime = fs::last_write_time(depfilename);
                if (deptime > time)
                    time = deptime;
            } catch (fs::filesystem_error &) {
                Yellow(cerr) << "Warning: Unable to determine modification "
                                "date of file \""
                             << depfilename << "\"\n"
                             << "         (dependency of " << source_dir / rpath
                             << ")" << std::endl;
            }
        return time;
    }

    bool is_resource_folder(const fs::directory_entry &entry) {
        return entry.path().filename() == "images" ||
               entry.path().filename() == "resources";
    }

    using PageOrDir = std::variant<Page, PageDirectory>;

    static void sort_pages(std::span<std::unique_ptr<PageOrDir>> pages) {
        auto order = [](const std::unique_ptr<PageOrDir> &lhs,
                        const std::unique_ptr<PageOrDir> &rhs) {
            auto visitor = [](const auto &lhs, const auto &rhs) {
                int lhs_seq = lhs.getSequenceNumber(),
                    rhs_seq = rhs.getSequenceNumber();
                if (lhs_seq != rhs_seq)
                    return lhs_seq < rhs_seq;
                if (lhs.is_folder && !rhs.is_folder)
                    return true;
                return lhs.getTitle() < rhs.getTitle();
            };
            return std::visit(visitor, *lhs, *rhs);
        };
        std::sort(pages.begin(), pages.end(), order);
    }

    void load_page_file(const fs::directory_entry &file_entry, Page &page) {
        string content = read_file(file_entry.path());
        page.metadata = read_metadata(file_entry, content);
        auto [html, lineno] = read_html(file_entry, content);
        page.html = std::move(html);
        page.lineno = lineno;
        page.modified = file_entry.last_write_time();
        page.abs_source_path = file_entry;
        page.rel_path = fs::relative(file_entry, source_dir);
        page.depmodified = get_dep_modified(page.rel_path);
    }

    Page load_page_file(const fs::directory_entry &file) {
        Page page;
        load_page_file(file, page);
        return page;
    }

    void create_index_file(const path &directory, PageDirectory &result) {
        Yellow(cerr) << "Warning: " << directory
                     << " has no index.html → default index created" << endl;
        path index = directory / "index.html";
        std::ofstream index_file = index;
        string contents = metadata_template;
        Color(cerr, ANSIColors::magenta)
            << index.parent_path().filename() << endl;
        replace(contents, ":title:", index.parent_path().filename());
        index_file << contents;
        index_file.close();
        load_page_file(fs::directory_entry(index), result);
    }

    void load_page_directory(const path &directory, PageDirectory &result) {
        bool hasIndex = false;
        for (const auto &entry : fs::directory_iterator(directory)) {
            if (entry.is_directory()) {
                if (is_resource_folder(entry)) {
                    result.resources.push_back(fs::relative(entry, source_dir));
                } else {
                    auto &dir = result.pages_and_subdirs.emplace_back(
                        std::make_unique<PageOrDir>(
                            std::in_place_type<PageDirectory>));
                    load_page_directory(entry, std::get<PageDirectory>(*dir));
                }
            } else if (entry.is_regular_file()) {
                if (entry.path().filename() == "index.html") {
                    load_page_file(entry, result);
                    hasIndex = true;
                } else {
                    result.pages_and_subdirs.emplace_back(
                        std::make_unique<PageOrDir>(load_page_file(entry)));
                }
            }
        }
        sort_pages(result.pages_and_subdirs);
        if (!hasIndex)
            create_index_file(directory, result);

        auto get_addr = [](PageOrDir &p) {
            auto visitor = [](auto &p) -> Page * { return &p; };
            return std::visit(visitor, p);
        };
        auto set_next = [](PageOrDir &p, Page *next) {
            auto visitor = [&](auto &p) { p.next = next; };
            return std::visit(visitor, p);
        };
        auto set_prev = [](PageOrDir &p, Page *previous) {
            auto visitor = [&](auto &p) { p.previous = previous; };
            return std::visit(visitor, p);
        };
        auto set_parent = [](PageOrDir &p, Page *parent) {
            auto visitor = [&](auto &p) { p.parent = parent; };
            return std::visit(visitor, p);
        };
        auto set_section = [](PageOrDir &p, int s) {
            auto visitor = [s](auto &p) { return p.sectionNumber = s; };
            return std::visit(visitor, p);
        };

        // Add the "next" and "previous" pointers to all pages in this directory
        if (result.pages_and_subdirs.size() > 1) {
            set_next(*result.pages_and_subdirs[0],
                     get_addr(*result.pages_and_subdirs[1]));
            for (size_t i = 1; i < result.pages_and_subdirs.size() - 1; ++i) {
                set_next(*result.pages_and_subdirs[i],
                         get_addr(*result.pages_and_subdirs[i + 1]));
                set_prev(*result.pages_and_subdirs[i],
                         get_addr(*result.pages_and_subdirs[i - 1]));
            }
            set_prev(*result.pages_and_subdirs.end()[-1],
                     get_addr(*result.pages_and_subdirs.end()[-2]));
        }
        // Add the "up" pointer to the pages in the subdirectoriesfor
        for (auto &dir : result.pages_and_subdirs) {
            overloaded visitor{
                [&set_parent](PageDirectory &dir) {
                    for (auto &page : dir.pages_and_subdirs)
                        set_parent(*page, &dir);
                },
                [](Page &) {},
            };
            std::visit(visitor, *dir);
        }
        // Add the section numbers
        if (auto secStart = result.getStartSectionNumber()) {
            int counter = *secStart;
            for (auto &entry : result.pages_and_subdirs)
                set_section(*entry, counter++);
        }
    }
#pragma endregion

  private:
    PageDirectory root;
    path source_dir;
    path output_dir;
    path template_dir;
    string metadata_template;
    vector<string> metadata_keys;
    string mathjax_template;
    string page_template;
    string index_template;
    string index_item_template;
    string index_item_folder_template;
};

path source_dir = "/home/pieter/GitHub/tttapa.github.io/Pages-src/Raw-HTML";
// path output_dir   = "/tmp";
path output_dir = "/home/pieter/GitHub/tttapa.github.io/Pages";
path template_dir = "/home/pieter/GitHub/tttapa.github.io/Pages-src/templates";

int main(int argc, const char *argv[]) {
    PagesParser p = {source_dir, output_dir, template_dir};
    p.load();
    if (argc > 1)
        p.exportAll(PagesParser::ServerSideLaTeXPDF, std::atoi(argv[1]));
    else
        p.exportAll();
    cout << "=== Done ===" << endl;
}