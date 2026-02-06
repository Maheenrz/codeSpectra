class Solution {
public:
    int f(int i, vector<int>& nums, vector<int>& dp) {
        int n = nums.size();
        if(i == n) return 0;
        if(dp[i] != INT_MIN) return dp[i];
        return dp[i] = max(nums[i] + f(i+1, nums, dp), nums[i]);
    }
    int maxSubArray(vector<int>& nums) {
        int n = nums.size();
        vector<int> dp(n+1, INT_MIN);
        int maxSum = nums[0];
        for(int i = 0; i < n; i++) {
            maxSum = max(maxSum, f(i, nums, dp));
        }
        return maxSum;
    }
};