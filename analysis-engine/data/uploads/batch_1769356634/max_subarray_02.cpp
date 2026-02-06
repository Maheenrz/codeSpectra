class Solution {
public:
    int maxSubArray(vector<int>& nums) {

        // Kadanes algorithm says that whenever the sum=0 which you have taken at the start goes less than 0, just again consider the sum as =0 and keep on adding the values as if we keep sum<0 (negative) and go forward adding, it will only hamper the sum value and we will not be able to find the maximum sum of the subarray
        int sum = 0, maxi=INT_MIN ;
        for ( int i =0 ; i <nums.size(); i++)
        {
            sum = sum + nums[i];
            maxi = max(sum, maxi);

            if(sum<0)
            {
                sum = 0; // crux of the kadanes algo (most optimal approach)
            }

        }
        return maxi;
    }
};