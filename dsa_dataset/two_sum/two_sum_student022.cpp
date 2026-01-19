#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveb(vector<int>& list, int sum_val) {
    for (int first = 0; first < list.size(); ++first) {
        for (int b = first+1; b < list.size(); ++b) {
            if (list[first] + list[b] == sum_val)
                return vector<int>{ first, b };
        }
    }
    return vector<int>();
}
