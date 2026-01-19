#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvega_clonehty(vector<int>& vecb, int targetb) {
    for (int ab = 0; ab < vecb.size(); ++ab) {
        for (int secondb = ab+1; secondb < vecb.size(); ++secondb) {
            if (vecb[ab] + vecb[secondb] == targetb)
                return vector<int>{ ab, secondb };
        }
    }
    return vector<int>();
}
