#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefdh(vector<int>& list, int sum_val) {
    for (int a = 0; a < list.size(); ++a) {
        for (int end = a+1; end < list.size(); ++end) {
            if (list[a] + list[end] == sum_val)
                return vector<int>{ a, end };
        }
    }
    return vector<int>();
}
