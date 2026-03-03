// Student: Sara Khan | Q1: Bubble Sort
#include <iostream>
using namespace std;

void sortBubble(int data[], int size) {
    for (int pass = 0; pass < size - 1; pass++) {
        for (int idx = 0; idx < size - pass - 1; idx++) {
            if (data[idx] > data[idx + 1]) {
                int hold = data[idx];
                data[idx] = data[idx + 1];
                data[idx + 1] = hold;
            }
        }
    }
}

void displayArray(int data[], int size) {
    for (int idx = 0; idx < size; idx++)
        cout << data[idx] << " ";
    cout << endl;
}

int main() {
    int data[] = {64, 34, 25, 12, 22, 11, 90};
    int size = sizeof(data) / sizeof(data[0]);
    cout << "Before sorting: ";
    displayArray(data, size);
    sortBubble(data, size);
    cout << "After sorting: ";
    displayArray(data, size);
    return 0;
}