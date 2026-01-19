#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefdh_cloney(vector<int>& listc, int sum_valc) {
    for (int ac = 0; ac < listc.size(); ++ac) {
        for (int endc = ac+1; endc < listc.size(); ++endc) {
            if (listc[ac] + listc[endc] == sum_valc)
                return vector<int>{ ac, endc };
        }
    }
    return vector<int>();
}
