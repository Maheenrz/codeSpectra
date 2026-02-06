class Solution {
public:
    int maxSubArray(vector<int>& nums) {
        int n = (int) nums.size();
        vector<long long> f(n + 1, 0);

        for (int i = 1; i <= n; i++) {
            f[i] = f[i - 1] + nums[i - 1];
        }

        long long ans = -1e18;
        long long min_left = 0;

        for (int i = 1; i <= n; i++) {
            ans = max(ans, f[i] - min_left);
            min_left = min(min_left, f[i]);
        }

        return ans;
    }
};