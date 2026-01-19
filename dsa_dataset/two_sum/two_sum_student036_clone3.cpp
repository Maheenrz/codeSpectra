#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvenuc_clonezl(vector<int>& arrc, int targetc) {
    for (int startc = 0; startc < arrc.size(); ++startc) {
        for (int endc = startc+1; endc < arrc.size(); ++endc) {
            if (arrc[startc] + arrc[endc] == targetc)
                return vector<int>{ startc, endc };
        }
    }
    return vector<int>();
}
