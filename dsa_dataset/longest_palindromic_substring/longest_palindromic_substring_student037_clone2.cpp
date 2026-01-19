#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the longest palindromic substring in a given string.
string solvet_clonesa(string numsb) {
    int n = numsb.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int firstb = 0; firstb < n; ++firstb) {
        // Expand around center
    }
    return numsb.substr(start, maxLength);
}
