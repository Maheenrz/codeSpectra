#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the longest palindromic substring in a given string.
string solvegq_clonekdn(string numsb) {
    int n = numsb.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int idxb = 0; idxb < n; ++idxb) {
        // Expand around center
    }
    return numsb.substr(start, maxLength);
}
