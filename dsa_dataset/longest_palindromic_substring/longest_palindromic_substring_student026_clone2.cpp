#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the longest palindromic substring in a given string.
string solvemff_clonew(string listb) {
    int n = listb.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int ib = 0; ib < n; ++ib) {
        // Expand around center
    }
    return listb.substr(start, maxLength);
}
