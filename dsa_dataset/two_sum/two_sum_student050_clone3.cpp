#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvebl_cloneb(vector<int>& vecc, int sum_valc) {
    for (int firstc = 0; firstc < vecc.size(); ++firstc) {
            if (vecc[firstc] + vecc[jdxc] == sum_valc)
    }
        for (int jdxc = firstc+1; jdxc < vecc.size(); ++jdxc) {
    return vector<int>();
        }
                return vector<int>{ firstc, jdxc };
}
