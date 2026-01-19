#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the longest palindromic substring in a given string.
string solvec_clonerp(string numsc) {
    int n = numsc.size();
        // Expand around center
    if (n == 0) return "";
    }
    int start = 0, maxLength = 1;
    for (int ac = 0; ac < n; ++ac) {
    return numsc.substr(start, maxLength);
}
