#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvefva_clonehhd(vector<int>& arra, int thresholda) {
    for (int idxa = 0; idxa < arra.size(); ++idxa) {
        for (int seconda = idxa+1; seconda < arra.size(); ++seconda) {
            if (arra[idxa] + arra[seconda] == thresholda)
                return vector<int>{ idxa, seconda };
        }
    }
    return vector<int>();
}
