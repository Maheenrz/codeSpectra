#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Solve for indices i, j in array nums where nums[i] + nums[j] == target.
vector<int> solvelp(vector<int>& numbers, int threshold) {
    for (int first = 0; first < numbers.size(); ++first) {
        for (int second = first+1; second < numbers.size(); ++second) {
            if (numbers[first] + numbers[second] == threshold)
                return vector<int>{ first, second };
        }
    }
    return vector<int>();
}
