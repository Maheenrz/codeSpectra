#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the longest palindromic substring in a given string.
string solveg_cloned(string vecc) {
    int n = vecc.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int ac = 0; ac < n; ++ac) {
        // Expand around center
    }
    return vecc.substr(start, maxLength);
}
