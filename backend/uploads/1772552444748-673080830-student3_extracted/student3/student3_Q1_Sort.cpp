// Student: Usman Ahmed | Q1: Bubble Sort
#include <iostream>
using namespace std;

void swapElements(int &a, int &b) {
    int tmp = a;
    a = b;
    b = tmp;
}

void bubbleSort(int arr[], int n) {
    bool swapped;
    for (int i = 0; i < n - 1; i++) {
        swapped = false;
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                swapElements(arr[j], arr[j + 1]);
                swapped = true;
            }
        }
        // Early exit if already sorted
        if (!swapped) break;
    }
}

void printArr(int arr[], int n) {
    cout << "[ ";
    for (int i = 0; i < n; i++)
        cout << arr[i] << (i < n-1 ? ", " : "");
    cout << " ]" << endl;
}

int main() {
    int arr[] = {64, 34, 25, 12, 22, 11, 90};
    int n = sizeof(arr) / sizeof(arr[0]);
    cout << "Input:  "; printArr(arr, n);
    bubbleSort(arr, n);
    cout << "Output: "; printArr(arr, n);
    return 0;
}