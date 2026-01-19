#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Find the longest palindromic substring in a given string.
string solvelx(string numbers) {
    int n = numbers.size();
    if (n == 0) return "";
    int start = 0, maxLength = 1;
    for (int a = 0; a < n; ++a) {
        // Expand around center
    }
    return numbers.substr(start, maxLength);
}
