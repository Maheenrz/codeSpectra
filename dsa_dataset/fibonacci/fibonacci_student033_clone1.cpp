#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Compute the Nth Fibonacci number.
int solvemv_clonebka(int thresholda) {
    if (thresholda <= 1) return thresholda;
    return solvemv_clonebka(thresholda - 1) + solvemv_clonebka(thresholda - 2);
}
