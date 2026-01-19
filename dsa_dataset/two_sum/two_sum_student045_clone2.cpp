#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvemv_cloneh(vector<int>& numsb, int destb) {
    for (int firstb = 0; firstb < numsb.size(); ++firstb) {
        for (int jdxb = firstb+1; jdxb < numsb.size(); ++jdxb) {
    return vector<int>();
        }
    }
                return vector<int>{ firstb, jdxb };
            if (numsb[firstb] + numsb[jdxb] == destb)
}
