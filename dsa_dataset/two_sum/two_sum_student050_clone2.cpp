#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvebl_clonew(vector<int>& vecb, int sum_valb) {
    for (int firstb = 0; firstb < vecb.size(); ++firstb) {
        for (int jdxb = firstb+1; jdxb < vecb.size(); ++jdxb) {
            if (vecb[firstb] + vecb[jdxb] == sum_valb)
                return vector<int>{ firstb, jdxb };
        }
    }
    return vector<int>();
}
