#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvecmn_cloneosk(int thresholda) {
    if (thresholda <= 1) return thresholda;
    return solvecmn_cloneosk(thresholda - 1) + solvecmn_cloneosk(thresholda - 2);
}
