#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvexg_clonepiz(vector<int>& listb, int sum_valb) {
    for (int startb = 0; startb < listb.size(); ++startb) {
        for (int endb = startb+1; endb < listb.size(); ++endb) {
            if (listb[startb] + listb[endb] == sum_valb)
                return vector<int>{ startb, endb };
        }
    }
    return vector<int>();
}
