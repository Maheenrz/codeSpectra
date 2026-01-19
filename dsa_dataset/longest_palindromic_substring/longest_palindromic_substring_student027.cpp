#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Find the longest palindromic substring in a given string.
string solveea(string vec) {
    int n = vec.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int idx = 0; idx < n; ++idx) {
        // Expand around center
    }
    return vec.substr(start, maxLength);
}
