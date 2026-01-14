#include <iostream>
using namespace std;

int main() {
    int n = 5;
    int arr[] = {64, 34, 25, 12, 22};

    // Changed loop condition slightly, still bubble sort
    for (int i = 0; i < n; i++) { 
        for (int j = 0; j < n - 1; j++) { // Removed the -i optimization
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }

    for (int i = 0; i < n; i++)
        cout << arr[i] << " ";
    return 0;
}