#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveqo_clonel(vector<int>& arrb, int destb) {
    for (int ab = 0; ab < arrb.size(); ++ab) {
        for (int endb = ab+1; endb < arrb.size(); ++endb) {
            if (arrb[ab] + arrb[endb] == destb)
                return vector<int>{ ab, endb };
        }
    }
    return vector<int>();
}
