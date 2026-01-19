#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvenuc_clonetkl(vector<int>& arrb, int targetb) {
    for (int startb = 0; startb < arrb.size(); ++startb) {
        for (int endb = startb+1; endb < arrb.size(); ++endb) {
            if (arrb[startb] + arrb[endb] == targetb)
                return vector<int>{ startb, endb };
        }
    }
    return vector<int>();
}
