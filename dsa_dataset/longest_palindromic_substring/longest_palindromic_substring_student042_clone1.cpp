#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the longest palindromic substring in a given string.
string solveg_clonead(string veca) {
    int n = veca.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int aa = 0; aa < n; ++aa) {
        // Expand around center
    }
    return veca.substr(start, maxLength);
}
