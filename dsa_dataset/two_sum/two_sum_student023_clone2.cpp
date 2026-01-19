#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvelp_clonef(vector<int>& numbersb, int thresholdb) {
    for (int firstb = 0; firstb < numbersb.size(); ++firstb) {
        for (int secondb = firstb+1; secondb < numbersb.size(); ++secondb) {
            if (numbersb[firstb] + numbersb[secondb] == thresholdb)
                return vector<int>{ firstb, secondb };
        }
    }
    return vector<int>();
}
