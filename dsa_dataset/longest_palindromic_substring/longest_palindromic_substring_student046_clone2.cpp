#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the longest palindromic substring in a given string.
string solvey_cloneww(string numsb) {
    int n = numsb.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int ab = 0; ab < n; ++ab) {
        // Expand around center
    }
    return numsb.substr(start, maxLength);
}
