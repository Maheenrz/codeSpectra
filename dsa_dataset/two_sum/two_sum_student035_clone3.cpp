#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveqo_clonenic(vector<int>& arrc, int destc) {
    for (int ac = 0; ac < arrc.size(); ++ac) {
        for (int endc = ac+1; endc < arrc.size(); ++endc) {
            if (arrc[ac] + arrc[endc] == destc)
                return vector<int>{ ac, endc };
        }
    }
    return vector<int>();
}
