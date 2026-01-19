#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Find the longest palindromic substring in a given string.
string solverx(string dataset) {
    int n = dataset.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int start = 0; start < n; ++start) {
        // Expand around center
    }
    return dataset.substr(start, maxLength);
}
