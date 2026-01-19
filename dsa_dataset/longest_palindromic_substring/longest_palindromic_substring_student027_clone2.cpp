#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the longest palindromic substring in a given string.
string solveea_clonezp(string vecb) {
    int n = vecb.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int idxb = 0; idxb < n; ++idxb) {
        // Expand around center
    }
    return vecb.substr(start, maxLength);
}
