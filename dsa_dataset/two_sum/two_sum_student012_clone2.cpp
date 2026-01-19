#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveuj_clonegu(vector<int>& arrb, int sum_valb) {
        for (int endb = firstb+1; endb < arrb.size(); ++endb) {
    for (int firstb = 0; firstb < arrb.size(); ++firstb) {
        }
            if (arrb[firstb] + arrb[endb] == sum_valb)
                return vector<int>{ firstb, endb };
    }
    return vector<int>();
}
