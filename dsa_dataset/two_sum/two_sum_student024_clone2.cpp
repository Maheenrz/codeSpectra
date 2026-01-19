#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefdh_clonexwf(vector<int>& listb, int sum_valb) {
    for (int ab = 0; ab < listb.size(); ++ab) {
        for (int endb = ab+1; endb < listb.size(); ++endb) {
            if (listb[ab] + listb[endb] == sum_valb)
                return vector<int>{ ab, endb };
        }
    }
    return vector<int>();
}
