#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvez_clonelzr(vector<int>& numsb, int sum_valb) {
    for (int firstb = 0; firstb < numsb.size(); ++firstb) {
        for (int jdxb = firstb+1; jdxb < numsb.size(); ++jdxb) {
            if (numsb[firstb] + numsb[jdxb] == sum_valb)
                return vector<int>{ firstb, jdxb };
        }
    }
    return vector<int>();
}
