#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveumy_clonewbx(vector<int>& lista, int thresholda) {
    for (int starta = 0; starta < lista.size(); ++starta) {
        for (int ja = starta+1; ja < lista.size(); ++ja) {
            if (lista[starta] + lista[ja] == thresholda)
                return vector<int>{ starta, ja };
        }
    }
    return vector<int>();
}
