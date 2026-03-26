# detectors/type4/educational/problem_bank/harness_templates.py
"""
Code harness templates for each problem category and language.

A harness wraps student code so it can be tested with stdin/stdout
without modifying the student's algorithm function itself.

Strategy:
  1. Student source is read as text.
  2. Their `main()` is renamed to prevent duplicate-main link errors.
  3. The harness `main()` is appended at the bottom.
  4. The harness calls the student's algorithm function by the detected name.
  5. Inputs are read from stdin; outputs go to stdout in a normalized format.

The {FUNC_NAME} placeholder is filled in by io_executor.py after the
algorithm classifier has detected the student's function name.
"""

from typing import Dict


# ─────────────────────────────────────────────────────────────────────────────
# C++ harness templates
# ─────────────────────────────────────────────────────────────────────────────

CPP_SORT_ARRAY = r"""
// ── CodeSpectra I/O Harness (Sort Array) ────────────────────────────────────
// Forward declaration — student's sort function may have any name.
// {FUNC_NAME} is substituted at runtime.
#include <sstream>
#include <vector>

int main() {
    std::string line;
    if (!std::getline(std::cin, line)) return 1;

    std::istringstream iss(line);
    std::vector<int> v;
    int x;
    while (iss >> x) v.push_back(x);

    int n = (int)v.size();
    if (n == 0) return 1;

    {FUNC_NAME}(v.data(), n);

    for (int i = 0; i < n; i++) {
        if (i) std::cout << ' ';
        std::cout << v[i];
    }
    std::cout << '\n';
    return 0;
}
"""

CPP_STACK_CLASS = r"""
// ── CodeSpectra I/O Harness (Stack, OOP class) ──────────────────────────────
// {CLASS_NAME} is substituted at runtime with detected class name.
// Method names push/pop/peek/isEmpty/size are detected and mapped.
int main() {
    {CLASS_NAME} __stack__;
    std::string op;
    while (std::cin >> op) {
        if (op == "PUSH") {
            int v; std::cin >> v;
            __stack__.{PUSH_METHOD}(v);
            std::cout << "OK\n";
        } else if (op == "POP") {
            std::cout << __stack__.{POP_METHOD}() << '\n';
        } else if (op == "PEEK") {
            std::cout << __stack__.{PEEK_METHOD}() << '\n';
        } else if (op == "SIZE") {
            std::cout << __stack__.{SIZE_METHOD}() << '\n';
        } else if (op == "ISEMPTY") {
            std::cout << (__stack__.{ISEMPTY_METHOD}() ? 1 : 0) << '\n';
        }
    }
    return 0;
}
"""

CPP_STACK_PROCEDURAL = r"""
// ── CodeSpectra I/O Harness (Stack, procedural struct) ──────────────────────
// {STRUCT_NAME}, {INIT_FUNC}, {PUSH_FUNC}, {POP_FUNC}, {PEEK_FUNC},
// {SIZE_FUNC}, {ISEMPTY_FUNC} are substituted at runtime.
int main() {
    {STRUCT_NAME} __stack__;
    {INIT_FUNC}(__stack__);
    std::string op;
    while (std::cin >> op) {
        if (op == "PUSH") {
            int v; std::cin >> v;
            {PUSH_FUNC}(__stack__, v);
            std::cout << "OK\n";
        } else if (op == "POP") {
            std::cout << {POP_FUNC}(__stack__) << '\n';
        } else if (op == "PEEK") {
            std::cout << {PEEK_FUNC}(__stack__) << '\n';
        } else if (op == "SIZE") {
            std::cout << {SIZE_FUNC}(__stack__) << '\n';
        } else if (op == "ISEMPTY") {
            std::cout << ({ISEMPTY_FUNC}(__stack__) ? 1 : 0) << '\n';
        }
    }
    return 0;
}
"""

CPP_LINKED_LIST_CLASS = r"""
// ── CodeSpectra I/O Harness (Linked List, OOP) ──────────────────────────────
int main() {
    {CLASS_NAME} __list__;
    std::string op;
    while (std::cin >> op) {
        if (op == "INSERT_END") {
            int v; std::cin >> v;
            __list__.{INSERT_END_METHOD}(v);
            std::cout << "OK\n";
        } else if (op == "INSERT_FRONT") {
            int v; std::cin >> v;
            __list__.{INSERT_FRONT_METHOD}(v);
            std::cout << "OK\n";
        } else if (op == "DELETE") {
            int v; std::cin >> v;
            __list__.{DELETE_METHOD}(v);
            std::cout << "OK\n";
        } else if (op == "SEARCH") {
            int v; std::cin >> v;
            // search returns bool or int — either works
            auto r = __list__.{SEARCH_METHOD}(v);
            std::cout << (r ? 1 : 0) << '\n';
        } else if (op == "LENGTH") {
            std::cout << __list__.{LENGTH_METHOD}() << '\n';
        } else if (op == "PRINT") {
            __list__.{PRINT_METHOD}();
            // output printed directly by student's display function;
            // normalizer will extract numbers
        }
    }
    return 0;
}
"""

CPP_LINEAR_SEARCH = r"""
// ── CodeSpectra I/O Harness (Linear Search) ─────────────────────────────────
#include <sstream>
#include <vector>
int main() {
    std::string line;
    if (!std::getline(std::cin, line)) return 1;
    std::istringstream iss(line);
    std::vector<int> v;
    int x; while (iss >> x) v.push_back(x);
    int target;
    if (!(std::cin >> target)) return 1;
    int idx = {FUNC_NAME}(v.data(), (int)v.size(), target);
    std::cout << idx << '\n';
    return 0;
}
"""

CPP_BINARY_SEARCH = r"""
// ── CodeSpectra I/O Harness (Binary Search) ─────────────────────────────────
#include <sstream>
#include <vector>
int main() {
    std::string line;
    if (!std::getline(std::cin, line)) return 1;
    std::istringstream iss(line);
    std::vector<int> v;
    int x; while (iss >> x) v.push_back(x);
    int target;
    if (!(std::cin >> target)) return 1;
    int idx = {FUNC_NAME}(v.data(), (int)v.size(), target);
    std::cout << idx << '\n';
    return 0;
}
"""

CPP_FIBONACCI = r"""
// ── CodeSpectra I/O Harness (Fibonacci) ─────────────────────────────────────
int main() {
    int n;
    if (!(std::cin >> n)) return 1;
    std::cout << {FUNC_NAME}(n) << '\n';
    return 0;
}
"""

CPP_FACTORIAL = r"""
// ── CodeSpectra I/O Harness (Factorial) ─────────────────────────────────────
int main() {
    int n;
    if (!(std::cin >> n)) return 1;
    // Use long long in case student returns long
    std::cout << (long long){FUNC_NAME}(n) << '\n';
    return 0;
}
"""

CPP_GCD = r"""
// ── CodeSpectra I/O Harness (GCD) ───────────────────────────────────────────
int main() {
    int a, b;
    if (!(std::cin >> a >> b)) return 1;
    std::cout << {FUNC_NAME}(a, b) << '\n';
    return 0;
}
"""

CPP_IS_PALINDROME = r"""
// ── CodeSpectra I/O Harness (Is Palindrome) ─────────────────────────────────
#include <string>
int main() {
    std::string s;
    if (!(std::cin >> s)) return 1;
    auto r = {FUNC_NAME}(s);
    std::cout << (r ? 1 : 0) << '\n';
    return 0;
}
"""

CPP_STRING_REVERSE = r"""
// ── CodeSpectra I/O Harness (String Reverse) ────────────────────────────────
#include <string>
int main() {
    std::string s;
    if (!(std::cin >> s)) return 1;
    // student may return string OR modify in-place
    auto result = {FUNC_NAME}(s);
    // if student returns void, s is modified in-place
    // if returns string, print that; otherwise print s
    std::cout << result << '\n';
    return 0;
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Python harness templates
# ─────────────────────────────────────────────────────────────────────────────

PYTHON_SORT_ARRAY = r"""
# ── CodeSpectra I/O Harness (Sort Array, Python) ─────────────────────────────
import sys

def __cs_main__():
    line = sys.stdin.readline().strip()
    if not line:
        return
    arr = list(map(int, line.split()))
    {FUNC_NAME}(arr)
    print(' '.join(map(str, arr)))

__cs_main__()
"""

PYTHON_FIBONACCI = r"""
# ── CodeSpectra I/O Harness (Fibonacci, Python) ──────────────────────────────
import sys

def __cs_main__():
    n = int(sys.stdin.readline().strip())
    print({FUNC_NAME}(n))

__cs_main__()
"""

PYTHON_FACTORIAL = r"""
# ── CodeSpectra I/O Harness (Factorial, Python) ──────────────────────────────
import sys

def __cs_main__():
    n = int(sys.stdin.readline().strip())
    print({FUNC_NAME}(n))

__cs_main__()
"""

PYTHON_GCD = r"""
# ── CodeSpectra I/O Harness (GCD, Python) ────────────────────────────────────
import sys

def __cs_main__():
    a, b = map(int, sys.stdin.readline().strip().split())
    print({FUNC_NAME}(a, b))

__cs_main__()
"""

# ─────────────────────────────────────────────────────────────────────────────
# Java harness templates
# ─────────────────────────────────────────────────────────────────────────────

JAVA_SORT_ARRAY = r"""
// ── CodeSpectra I/O Harness (Sort Array, Java) ───────────────────────────────
// Appended after student class; calls their static sort method.
class __CSHarness__ {
    public static void main(String[] args) throws Exception {
        java.util.Scanner sc = new java.util.Scanner(System.in);
        String line = sc.nextLine().trim();
        String[] parts = line.split("\\s+");
        int[] arr = new int[parts.length];
        for (int i = 0; i < parts.length; i++)
            arr[i] = Integer.parseInt(parts[i]);
        // Call student's sort method (static in student class)
        {CLASS_NAME}.{FUNC_NAME}(arr, arr.length);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < arr.length; i++) {
            if (i > 0) sb.append(' ');
            sb.append(arr[i]);
        }
        System.out.println(sb);
    }
}
"""

JAVA_FIBONACCI = r"""
// ── CodeSpectra I/O Harness (Fibonacci, Java) ────────────────────────────────
class __CSHarness__ {
    public static void main(String[] args) throws Exception {
        java.util.Scanner sc = new java.util.Scanner(System.in);
        int n = sc.nextInt();
        System.out.println({CLASS_NAME}.{FUNC_NAME}(n));
    }
}
"""

JAVA_GCD = r"""
// ── CodeSpectra I/O Harness (GCD, Java) ─────────────────────────────────────
class __CSHarness__ {
    public static void main(String[] args) throws Exception {
        java.util.Scanner sc = new java.util.Scanner(System.in);
        int a = sc.nextInt(), b = sc.nextInt();
        System.out.println({CLASS_NAME}.{FUNC_NAME}(a, b));
    }
}
"""


# ─────────────────────────────────────────────────────────────────────────────
# Registry: maps (category, language) → harness template string
# ─────────────────────────────────────────────────────────────────────────────

HARNESS_TEMPLATES: Dict[str, Dict[str, str]] = {
    "SORT_ARRAY": {
        "cpp":    CPP_SORT_ARRAY,
        "python": PYTHON_SORT_ARRAY,
        "java":   JAVA_SORT_ARRAY,
    },
    "STACK_OOP": {
        "cpp": CPP_STACK_CLASS,
    },
    "STACK_PROCEDURAL": {
        "cpp": CPP_STACK_PROCEDURAL,
    },
    "LINKED_LIST": {
        "cpp": CPP_LINKED_LIST_CLASS,
    },
    "LINEAR_SEARCH": {
        "cpp": CPP_LINEAR_SEARCH,
    },
    "BINARY_SEARCH": {
        "cpp": CPP_BINARY_SEARCH,
    },
    "FIBONACCI": {
        "cpp":    CPP_FIBONACCI,
        "python": PYTHON_FIBONACCI,
        "java":   JAVA_FIBONACCI,
    },
    "FACTORIAL": {
        "cpp":    CPP_FACTORIAL,
        "python": PYTHON_FACTORIAL,
    },
    "GCD": {
        "cpp":    CPP_GCD,
        "python": PYTHON_GCD,
        "java":   JAVA_GCD,
    },
    "IS_PALINDROME": {
        "cpp": CPP_IS_PALINDROME,
    },
    "STRING_REVERSE": {
        "cpp": CPP_STRING_REVERSE,
    },
}


def get_harness_template(category: str, language: str) -> str | None:
    """
    Return the harness template string for the given (category, language) pair.
    Returns None if no template exists for that combination.
    """
    lang_map = HARNESS_TEMPLATES.get(category, {})
    return lang_map.get(language)
