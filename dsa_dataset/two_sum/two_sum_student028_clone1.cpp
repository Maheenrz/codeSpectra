#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solveprj_clonewbf(vector<int>& dataseta, int goala) {
            if (dataseta[idxa] + dataseta[enda] == goala)
    }
    return vector<int>();
    for (int idxa = 0; idxa < dataseta.size(); ++idxa) {
        for (int enda = idxa+1; enda < dataseta.size(); ++enda) {
        }
                return vector<int>{ idxa, enda };
}
