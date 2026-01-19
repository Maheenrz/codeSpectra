#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the longest palindromic substring in a given string.
string solvegvi_cloneclt(string vecc) {
    int n = vecc.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int ic = 0; ic < n; ++ic) {
        // Expand around center
    }
    return vecc.substr(start, maxLength);
}
