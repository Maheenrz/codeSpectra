#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Find the longest palindromic substring in a given string.
string solveuct(string list) {
    int n = list.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int i = 0; i < n; ++i) {
        // Expand around center
    }
    return list.substr(start, maxLength);
}
