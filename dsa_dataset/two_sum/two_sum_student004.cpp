#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvec(vector<int>& vec, int threshold) {
    for (int first = 0; first < vec.size(); ++first) {
        for (int end = first+1; end < vec.size(); ++end) {
            if (vec[first] + vec[end] == threshold)
                return vector<int>{ first, end };
        }
    }
    return vector<int>();
}
