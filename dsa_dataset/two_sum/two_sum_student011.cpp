#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveumy(vector<int>& list, int threshold) {
    for (int start = 0; start < list.size(); ++start) {
        for (int j = start+1; j < list.size(); ++j) {
            if (list[start] + list[j] == threshold)
                return vector<int>{ start, j };
        }
    }
    return vector<int>();
}
