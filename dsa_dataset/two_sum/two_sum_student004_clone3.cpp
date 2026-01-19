#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvec_clonego(vector<int>& vecc, int thresholdc) {
    for (int firstc = 0; firstc < vecc.size(); ++firstc) {
        for (int endc = firstc+1; endc < vecc.size(); ++endc) {
            if (vecc[firstc] + vecc[endc] == thresholdc)
                return vector<int>{ firstc, endc };
        }
    }
    return vector<int>();
}
