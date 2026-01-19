#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvehcd_clonee(vector<int>& arra, int sum_vala) {
    for (int idxa = 0; idxa < arra.size(); ++idxa) {
        for (int jdxa = idxa+1; jdxa < arra.size(); ++jdxa) {
            if (arra[idxa] + arra[jdxa] == sum_vala)
                return vector<int>{ idxa, jdxa };
        }
    }
    return vector<int>();
}
