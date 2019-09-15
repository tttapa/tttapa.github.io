#include <cassert>
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
#include <sstream>
#include <string>
#include <vector>

#include <pybind11/embed.h>
#include <pybind11/stl.h>

#include "ANSIColors.hpp"
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

using string_map  = std::map<string, string>;
using file_time_t = std::filesystem::file_time_type;

class PagesParser {
  public:
    struct Page {
        string_map metadata;
        string html;
        unsigned int lineno; ///< line number where <html> starts
        file_time_t modified;
        path abs_source_path;
        path rel_path;

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
    };

    struct PageDirectory : public Page {
        vector<Page> pages;
        vector<PageDirectory> subdirectories;
        vector<path> resources;
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
        root = load_page_directory(source_dir);
    }

    Task task;

    void exportAll(Task task = ClientSideLaTeX, unsigned int num_threads = 0) {
        py::scoped_interpreter interpreter{};
        path file      = __FILE__;
        path folder    = file.parent_path();
        py::module sys = py::module::import("sys");
        sys.attr("path").cast<py::list>().append(folder.string());
        py::globals()["HTMLFormatter"] = py::module::import("HTMLFormatter");
        this->task                     = task;
        if ((task == ServerSideLaTeX || task == ServerSideLaTeXPDF) &&
            num_threads <= 0)
            num_threads = 2 * std::thread::hardware_concurrency();
        if (task == ServerSideLaTeX || task == ServerSideLaTeXPDF) {
            assert(num_threads > 0);
            this->mjpage_futures.resize(num_threads);
        }
        if (task == ServerSideLaTeXPDF)
            startHTTPandChromeServers();
        exportDirectory(root);
        if (task == ServerSideLaTeX || task == ServerSideLaTeXPDF)
            wait_all_mjpage();
        // cout << "LaTeX compilation done" << endl;
        if (task == ServerSideLaTeXPDF)
            exportPDFDirectory(root);
    }

  private:
    const int dev_port  = 9222;
    const int http_port = 5741;

    const path tmp_dir = "/tmp/Pages";

    vector<std::future<const Page &>> mjpage_futures = {};

    void startHTTPandChromeServers() {
        string c = "cd \"" + output_dir.parent_path().string() +
                   "\" && python3 -m http.server " + std::to_string(http_port) +
                   " --bind 127.0.0.1 &";
        cout << c << endl;
        if (system(c.c_str()) != 0) {
        }  // TODO
        c = "google-chrome --headless --disable-gpu "
            "--run-all-compositor-stages-before-draw --remote-debugging-port=" +
            std::to_string(dev_port) + " &";
        cout << c << endl;
        if (system(c.c_str()) != 0) {
        }  // TODO
    }

    void handle_finished_mjpage(const Page &page) {
        Green(cout) << "Page `" << page.getTitle() << "` finished" << endl;
    }

    void export_mjpage(const Page &page, const string &out) {
        using namespace std::chrono_literals;
        fs::create_directories(tmp_dir / page.rel_path.parent_path());
        fs::create_directories(output_dir / page.rel_path.parent_path());
        std::ofstream outfile(tmp_dir / page.rel_path);
        outfile << out;
        outfile.close();
        string command = "mjpage";
        command += " --output=CommonHTML --eqno=AMS "
                   "--fontURL=/MathJax/fonts/HTML-CSS";
        command += " < \"";
        command += tmp_dir / page.rel_path;
        command += "\" > \"";
        command += output_dir / page.rel_path;
        command += "\"";

        bool launched            = false;
        const Page *finishedPage = nullptr;
        while (!launched) {
            for (auto &fut : mjpage_futures) {
                if (fut.valid() == false ||  // uninitialized
                    fut.wait_for(10ms) == std::future_status::ready) {
                    finishedPage = fut.valid() ? &(fut.get()) : nullptr;
                    Blue(cout) << "Started compiling Page `" << page.getTitle()
                               << "`" << endl;
                    auto launch = [command, &page]() -> const Page & {
                        if (system(command.c_str()) != 0) {
                        }  // TODO
                        return page;
                    };
                    fut      = std::async(std::launch::async, launch);
                    launched = true;
                    break;  // for
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
                if (fut.valid() == false ||  // uninitialized
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

    /**
     * @brief   Export a regular page.
     */
    void exportPage(const Page &page) {
        string out = createPage(page, page_template);
        bool hasLaTeX =
            out.find("\\(") != string::npos || out.find("$$") != string::npos;
        if ((task == ServerSideLaTeX || task == ServerSideLaTeXPDF) &&
            hasLaTeX) {
            export_mjpage(page, out);
        } else {
            Green(cout) << "Exporting page `" << page.getTitle() << "`" << endl;
            std::ofstream outfile(output_dir / page.rel_path);
            outfile << out;
        }
    }

    /**
     * @brief   Export the index page of a directory.
     */
    void exportPage(const PageDirectory &page) {
        string out = createPage(page, index_template);
        replace(out, ":index:", generateIndex(page));
        std::ofstream outfile(output_dir / page.rel_path);
        outfile << out;
    }

    string createPage(const Page &page, string pageTemplate) {
        string out = pageTemplate;
        replace(out, ":title:", page.getTitle());
        replace(out, ":nav:", generateNavigation(page));
        replace(out, ":filenamepdf:", page.rel_path.stem().string() + ".pdf");
        string html = page.html;
        replace(out, ":html:",
                formatHTML(page.html, page.abs_source_path, page.lineno));
        replace(out, ":mdate:", formatFileTime(page.modified));
        for (const auto &[key, value] : page.metadata)
            while (replace(out, ":" + key + ":", value))
                ;
        return out;
    }

    void exportDirectory(const PageDirectory &dir) {
        // Create the folder structure in the output directory
        fs::create_directories(output_dir / dir.rel_path.parent_path());
        // Copy all resource folders
        for (auto &dir : dir.resources)
            fs::copy(source_dir / dir, output_dir / dir,
                     fs::copy_options::overwrite_existing |
                         fs::copy_options::recursive);
        // Export the index page of the current directory
        exportPage(dir);
        // Export all subdirectories
        for (auto &subdir : dir.subdirectories)
            exportDirectory(subdir);
        // Export all other pages in this directory
        for (auto &page : dir.pages)
            exportPage(page);
    }

    void exportPDFPage(const Page &page) {
        path pdf_file = output_dir / page.rel_path;
        pdf_file.replace_extension(".pdf");
        if (fs::exists(pdf_file) &&
            page.modified <= fs::last_write_time(pdf_file))
            return;
        path file      = __FILE__;
        path folder    = file.parent_path();
        string command = "cd \"";
        command += folder;
        command += "\" && ";
        command += "./print-to-pdf.js ";
        command += std::to_string(dev_port);
        command += " \"";
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
            Red(cerr) << "print-to-pdf.js for `" << page.getTitle()
                      << "` failed with exit status " << status << endl;
        }
    }

    void exportPDFDirectory(const PageDirectory &dir) {
        // Export the index page of the current directory
        exportPDFPage(dir);
        // Export all subdirectories
        for (auto &subdir : dir.subdirectories)
            exportPDFDirectory(subdir);
        // Export all other pages in this directory
        for (auto &page : dir.pages)
            exportPDFPage(page);
    }

    static bool isPageToList(const Page &page) {
        string filename = page.rel_path.filename();
        return filename[0] != '.';
    }

    static bool isDirectoryToList(const PageDirectory &dir) {
        string dirname = dir.rel_path.parent_path().filename();
        return dirname[0] != '.';
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
        for (const auto &entry : root.subdirectories) {
            if (!isDirectoryToList(entry))
                continue;
            bool open_entry = page.rel_path == entry.rel_path;
            string rel =
                fs::relative(page.rel_path, entry.rel_path.parent_path());
            bool expanded = rel.substr(0, 2) != "..";
            result += indentation_li;
            result += "<li";
            if (expanded)
                result += " class=\"expanded\"";
            result += ">";
            result += "<span class=\"dtriangle\" "
                      "onclick=\"this.parentElement.classList.toggle('"
                      "expanded');\">"
                      "</span>";
            result += "<a";
            if (open_entry)
                result += " class=\"openEntry\"";
            result += " href=\"";
            result += fs::relative(entry.rel_path, page.rel_path.parent_path());
            result += "\">";
            result += entry.getTitle();
            result += "</a>\n";
            result += generateNavigation(page, entry, level + 1);
            result += indentation_li;
            result += "</li>\n";
        }
        for (const auto &entry : root.pages) {
            if (!isPageToList(entry))
                continue;
            string rel      = fs::relative(page.rel_path, entry.rel_path);
            bool open_entry = rel == ".";
            result += indentation_li;
            result += "<li><span class=\"ftriangle\"></span>";
            result += "<a";
            if (open_entry)
                result += " class=\"openEntry\"";
            result += " href=\"";
            result += fs::relative(entry.rel_path, page.rel_path.parent_path());
            result += "\">";
            result += entry.getTitle();
            result += "</a></li>\n";
        }
        result += indentation_ul;
        result += "</ul>\n";
        return result;
    }

    string generateIndexItem(const Page &page, const path &root) {
        string item = index_item_template;
        replace(item, ":title:", page.getTitle());
        replace(item, ":link:", fs::relative(page.rel_path, root));
        replace(item, ":description:", page.getDescription());
        return item;
    }

    string generateIndex(const PageDirectory &dir) {
        string result;
        for (const auto &entry : dir.subdirectories) {
            if (!isDirectoryToList(entry))
                continue;
            result += generateIndexItem(entry, dir.rel_path.parent_path());
        }
        for (const auto &entry : dir.pages) {
            if (!isPageToList(entry))
                continue;
            result += generateIndexItem(entry, dir.rel_path.parent_path());
        }
        return result;
    }

  private:
#pragma region HTML formatter...................................................

    string formatHTML(const string &html, const fs::path &path,
                      unsigned int lineno) {
        auto formatHTML = py::globals()["HTMLFormatter"].attr("formatHTML");
        return formatHTML(html, path.string(), lineno).cast<string>();
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
        if (size_t start = str.find(from); start != string::npos) {
            str.replace(start, from.length(), to);
            return true;
        }
        return false;
    }

    static string formatFileTime(std::filesystem::file_time_type ft) {
        std::stringstream buffer;
        std::time_t tt = ft.time_since_epoch().count() / 1'000'000'000 +
                         6'437'664'000;  // TODO: ugly non-portable hack
        std::tm *gmt = std::gmtime(&tt);
        buffer << std::put_time(gmt, "%A, %d %B %Y %H:%M");
        return buffer.str();
    }

#pragma endregion
#pragma region Loading source files.............................................

    void init() {
        load_template();
        page_template  = read_file(template_dir / "template.html");
        index_template = read_file(template_dir / "template_index.html");
        index_item_template =
            read_file(template_dir / "template_index_item.html");
    }

    static string read_file(path filename) {
        ifstream file = filename;
        string contents;
        std::getline(file, contents, '\0');
        return contents;
    }

    void load_template() {
        metadata_template = read_file(template_dir / "template_meta.html");
        string comment    = get_first_comment(metadata_template);
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
        auto first_match              = comment.find("\n@" + key + ':');
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
        size_t start  = content.find("<html>");
        size_t end    = content.rfind("</html>");
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
        string_map dict;
        string comment = get_first_comment(content);
        for (const auto &key : metadata_keys) {
            auto value = read_metadata_value(comment, key);
            if (value) {
                dict[key] = *value;
            } else if (key != "sequence") {
                Yellow(cerr) << "Warning: missing value for key `" << key
                             << "` for " << file_entry << endl;
                (void) file_entry;
            }
        }
        return dict;
    }

    bool is_resource_folder(const fs::directory_entry &entry) {
        return entry.path().filename() == "images" ||
               entry.path().filename() == "resources";
    }

    template <class Page>
    static void sort_pages(vector<Page> &pages) {
        auto order = [](const Page &lhs, const Page &rhs) {
            int lhs_seq = lhs.getSequenceNumber(),
                rhs_seq = rhs.getSequenceNumber();
            if (lhs_seq != rhs_seq)
                return lhs_seq < rhs_seq;
            else
                return lhs.getTitle() < rhs.getTitle();
        };
        std::sort(pages.begin(), pages.end(), order);
    }

    void load_page_file(const fs::directory_entry &file_entry, Page &page) {
        string content       = read_file(file_entry.path());
        page.metadata        = read_metadata(file_entry, content);
        auto [html, lineno]  = read_html(file_entry, content);
        page.html            = html;
        page.lineno          = lineno;
        page.modified        = file_entry.last_write_time();
        page.abs_source_path = file_entry;
        page.rel_path        = fs::relative(file_entry, source_dir);
    }

    Page load_page_file(const fs::directory_entry &file) {
        Page page;
        load_page_file(file, page);
        return page;
    }

    void create_index_file(const path &directory, PageDirectory &result) {
        Yellow(cerr) << "Warning: " << directory
                     << " has no index.html → default index created" << endl;
        path index               = directory / "index.html";
        std::ofstream index_file = index;
        string contents          = metadata_template;
        Color(cerr, ANSIColors::magenta)
            << index.parent_path().filename() << endl;
        replace(contents, ":title:", index.parent_path().filename());
        index_file << contents;
        index_file.close();
        load_page_file(fs::directory_entry(index), result);
    }

    PageDirectory load_page_directory(const path &directory) {
        PageDirectory result;
        bool hasIndex = false;
        for (const auto &entry : fs::directory_iterator(directory)) {
            if (entry.is_directory()) {
                if (is_resource_folder(entry)) {
                    result.resources.push_back(fs::relative(entry, source_dir));
                } else {
                    result.subdirectories.push_back(load_page_directory(entry));
                }
            } else if (entry.is_regular_file()) {
                if (entry.path().filename() == "index.html") {
                    load_page_file(entry, result);
                    hasIndex = true;
                } else {
                    result.pages.push_back(load_page_file(entry));
                }
            }
        }
        sort_pages(result.pages);
        sort_pages(result.subdirectories);
        if (!hasIndex)
            create_index_file(directory, result);
        /*
        cout << __func__ << endl << result.getTitle() << endl;
        for (auto &[key, value] : result.metadata)
            cout << key << " → " << value << endl;
        cout << endl; 
        // */
        return result;
    }
#pragma endregion

  private:
    PageDirectory root;
    path source_dir;
    path output_dir;
    path template_dir;
    string metadata_template;
    vector<string> metadata_keys;
    string page_template;
    string index_template;
    string index_item_template;
};

path source_dir = "/home/pieter/GitHub/tttapa.github.io/Pages-src/Raw-HTML";
// path output_dir   = "/tmp";
path output_dir   = "/home/pieter/GitHub/tttapa.github.io/Pages";
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