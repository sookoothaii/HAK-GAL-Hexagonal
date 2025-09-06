#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <vector>
#include <regex>
#include <unordered_set>

namespace py = pybind11;

static bool validate_one(const std::string &s) {
    static const std::regex pattern(R"(^[A-Za-z_][A-Za-z0-9_]*\([^,\)]+,\s*[^\)]+\)\.\s*$)");
    return std::regex_match(s, pattern);
}

static std::vector<bool> validate_facts_batch(const std::vector<std::string> &statements) {
    std::vector<bool> out;
    out.reserve(statements.size());
    for (const auto &s : statements) {
        out.push_back(validate_one(s));
    }
    return out;
}

static std::vector<std::tuple<int,int,double>> find_duplicates(const std::vector<std::string> &statements, double threshold) {
    auto clamp = [](double v){ return v < 0.0 ? 0.0 : (v > 1.0 ? 1.0 : v); };
    const double thr = clamp(threshold);
    const int n = static_cast<int>(statements.size());
    std::vector<std::unordered_set<std::string>> toks;
    toks.reserve(n);
    std::regex token_re(R"([A-Za-z0-9_]+)");
    for (const auto &s : statements) {
        std::unordered_set<std::string> tset;
        auto begin = std::sregex_iterator(s.begin(), s.end(), token_re);
        auto end = std::sregex_iterator();
        for (auto it = begin; it != end; ++it) {
            tset.insert(it->str());
        }
        toks.emplace_back(std::move(tset));
    }
    std::vector<std::tuple<int,int,double>> out;
    for (int i = 0; i < n; ++i) {
        if (toks[i].empty()) continue;
        for (int j = i + 1; j < n; ++j) {
            if (toks[j].empty()) continue;
            size_t inter = 0;
            const auto &A = toks[i];
            const auto &B = toks[j];
            for (const auto &tok : A) {
                if (B.find(tok) != B.end()) ++inter;
            }
            const size_t uni = A.size() + B.size() - inter;
            const double score = uni ? static_cast<double>(inter) / static_cast<double>(uni) : 0.0;
            if (score >= thr) {
                out.emplace_back(i, j, score);
            }
        }
    }
    return out;
}

PYBIND11_MODULE(mojo_kernels, m) {
    m.doc() = "mojo_kernels: pybind11 native extension for HAK-GAL";
    m.def("validate_facts_batch", &validate_facts_batch, "Batch fact validator");
    m.def("find_duplicates", &find_duplicates, py::arg("statements"), py::arg("threshold") = 0.95, "Duplicate finder (token Jaccard)");
}
