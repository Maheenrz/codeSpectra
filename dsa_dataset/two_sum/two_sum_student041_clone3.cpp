#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvexg_cloneit(vector<int>& listc, int sum_valc) {
    for (int startc = 0; startc < listc.size(); ++startc) {
        for (int endc = startc+1; endc < listc.size(); ++endc) {
                return vector<int>{ startc, endc };
        }
    }
            if (listc[startc] + listc[endc] == sum_valc)
    return vector<int>();
}
