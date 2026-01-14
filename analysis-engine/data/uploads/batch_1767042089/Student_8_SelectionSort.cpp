#include <iostream>
using namespace std;

int main() {
    int n = 5;
    int arr[] = {64, 34, 25, 12, 22};

    // Selection Sort Logic
    for (int i = 0; i < n-1; i++) {
        int min_idx = i;
        for (int j = i+1; j < n; j++)
            if (arr[j] < arr[min_idx])
                min_idx = j;
        
        // Swap found minimum element with first element
        int temp = arr[min_idx];
        arr[min_idx] = arr[i];
        arr[i] = temp;
    }

    for (int i = 0; i < n; i++) cout << arr[i] << " ";
    return 0;
}