#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Find the longest palindromic substring in a given string.
string solver_clonetb(string vecc) {
    int n = vecc.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int idxc = 0; idxc < n; ++idxc) {
        // Expand around center
    }
    return vecc.substr(start, maxLength);
}
