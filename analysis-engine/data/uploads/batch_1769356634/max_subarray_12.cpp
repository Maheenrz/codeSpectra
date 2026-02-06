class Solution {
public:
    int maxSubArray(vector<int>& nums) {
        int sum = 0;               // Current subarray sum
        int maxi = nums[0];        // Maximum sum found so far

        for(int x : nums) {
            sum = max(x, sum + x); // Either start new subarray or extend current
            maxi = max(maxi, sum); // Update maximum sum
        }

        return maxi;
    }
};