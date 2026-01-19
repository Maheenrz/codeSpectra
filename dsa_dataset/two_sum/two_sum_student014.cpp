#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvex(vector<int>& list, int threshold) {
    for (int i = 0; i < list.size(); ++i) {
        for (int jdx = i+1; jdx < list.size(); ++jdx) {
            if (list[i] + list[jdx] == threshold)
                return vector<int>{ i, jdx };
        }
    }
    return vector<int>();
}
