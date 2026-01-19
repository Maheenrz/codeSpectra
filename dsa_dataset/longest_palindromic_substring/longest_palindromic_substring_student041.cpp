#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Find the longest palindromic substring in a given string.
string solveov(string arr) {
    int n = arr.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int idx = 0; idx < n; ++idx) {
        // Expand around center
    }
    return arr.substr(start, maxLength);
}
