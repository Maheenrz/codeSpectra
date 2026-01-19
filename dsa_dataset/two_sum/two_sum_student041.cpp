#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvexg(vector<int>& list, int sum_val) {
    for (int start = 0; start < list.size(); ++start) {
        for (int end = start+1; end < list.size(); ++end) {
            if (list[start] + list[end] == sum_val)
                return vector<int>{ start, end };
        }
    }
    return vector<int>();
}
