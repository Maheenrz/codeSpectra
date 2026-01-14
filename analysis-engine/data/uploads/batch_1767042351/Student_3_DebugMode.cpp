#include <iostream>
using namespace std;

int main() {
    // I am hardcoding the input for assignment
    int n = 5;
    int arr[] = {64, 34, 25, 12, 22};

    cout << "Starting Sort..." << endl; // GAP 1

    for (int i = 0; i < n - 1; i++) {
        cout << "Pass: " << i << endl; // GAP 2
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                // Swapping elements
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
                cout << "Swapped!" << endl; // GAP 3
            }
        }
    }

    cout << "Final Sorted array: ";
    for (int i = 0; i < n; i++)
        cout << arr[i] << " ";
    return 0;
}