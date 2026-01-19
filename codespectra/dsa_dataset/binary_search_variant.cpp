// Sample C++ file: Binary Search (variant implementation)
#include <iostream>
#include <vector>

int searchBinary(std::vector<int>& nums, int value) {
    int start = 0;
    int end = nums.size() - 1;
    
    while (start <= end) {
        int middle = (start + end) / 2;
        
        if (nums[middle] == value) {
            return middle;
        }
        
        if (nums[middle] < value) {
            start = middle + 1;
        } else {
            end = middle - 1;
        }
    }
    
    return -1;
}

int main() {
    std::vector<int> data = {2, 4, 6, 8, 10, 12, 14, 16};
    int find = 10;
    
    int index = searchBinary(data, find);
    
    if (index != -1) {
        std::cout << "Found at position: " << index << std::endl;
    } else {
        std::cout << "Not found" << std::endl;
    }
    
    return 0;
}
