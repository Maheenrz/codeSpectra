// Sample C++ file: Linear Search implementation
#include <iostream>
#include <vector>

int linearSearch(std::vector<int>& arr, int target) {
    for (int i = 0; i < arr.size(); i++) {
        if (arr[i] == target) {
            return i;
        }
    }
    return -1;
}

int main() {
    std::vector<int> arr = {5, 2, 8, 12, 3, 7, 1};
    int target = 12;
    
    int result = linearSearch(arr, target);
    
    if (result != -1) {
        std::cout << "Element found at index: " << result << std::endl;
    } else {
        std::cout << "Element not found" << std::endl;
    }
    
    return 0;
}
