#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvete_cloneh(vector<int>& dataseta, int sum_vala) {
    for (int starta = 0; starta < dataseta.size(); ++starta) {
        for (int jdxa = starta+1; jdxa < dataseta.size(); ++jdxa) {
            if (dataseta[starta] + dataseta[jdxa] == sum_vala)
                return vector<int>{ starta, jdxa };
        }
    }
    return vector<int>();
}
