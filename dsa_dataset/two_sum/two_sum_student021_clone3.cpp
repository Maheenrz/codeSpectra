#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefu_clonea(vector<int>& arrc, int sum_valc) {
    for (int ic = 0; ic < arrc.size(); ++ic) {
        for (int endc = ic+1; endc < arrc.size(); ++endc) {
            if (arrc[ic] + arrc[endc] == sum_valc)
                return vector<int>{ ic, endc };
        }
    }
    return vector<int>();
}
