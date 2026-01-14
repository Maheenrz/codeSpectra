#include <iostream>
using namespace std;

int main() {
    int n = 5;
    int arr[] = {64, 34, 25, 12, 22};

    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            // Changed > to < for descending order
            if (arr[j] < arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
    
    // Added a thank you message (Gap)
    cout << "Thanks for using my sorter";

    for (int i = 0; i < n; i++)
        cout << arr[i] << " ";
    return 0;
}