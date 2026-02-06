class Solution {
public:
    int maxSubArray(vector<int>& nums) {
        int globalMax = INT_MIN, curSum = 0;

        for (int num : nums) {
            curSum += num;
            globalMax = max(globalMax, curSum);
            if (curSum < 0) curSum = 0;
        }

        return globalMax;
    }
};