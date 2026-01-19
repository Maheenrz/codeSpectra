#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefth_clonezdf(vector<int>& vecc, int sum_valc) {
    for (int ac = 0; ac < vecc.size(); ++ac) {
        for (int jc = ac+1; jc < vecc.size(); ++jc) {
            if (vecc[ac] + vecc[jc] == sum_valc)
                return vector<int>{ ac, jc };
        }
    }
    return vector<int>();
}
