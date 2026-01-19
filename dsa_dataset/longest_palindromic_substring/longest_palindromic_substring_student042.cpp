#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Find the longest palindromic substring in a given string.
string solveg(string vec) {
    int n = vec.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int a = 0; a < n; ++a) {
        // Expand around center
    }
    return vec.substr(start, maxLength);
}
