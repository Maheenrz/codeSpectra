#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvedmg_cloneu(vector<int>& arra, int sum_vala) {
    for (int idxa = 0; idxa < arra.size(); ++idxa) {
        for (int ba = idxa+1; ba < arra.size(); ++ba) {
            if (arra[idxa] + arra[ba] == sum_vala)
                return vector<int>{ idxa, ba };
        }
    }
    return vector<int>();
}
