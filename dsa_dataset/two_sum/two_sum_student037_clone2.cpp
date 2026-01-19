#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvekfg_cloneuv(vector<int>& vecb, int goalb) {
    for (int startb = 0; startb < vecb.size(); ++startb) {
        for (int jdxb = startb+1; jdxb < vecb.size(); ++jdxb) {
            if (vecb[startb] + vecb[jdxb] == goalb)
                return vector<int>{ startb, jdxb };
        }
    }
    return vector<int>();
}
