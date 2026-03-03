// Student: Fatima Malik | Q1: Sort Array (Selection Sort approach)
#include <iostream>
using namespace std;

void selectionSort(int numbers[], int count) {
    for (int i = 0; i < count - 1; i++) {
        int minIndex = i;
        for (int j = i + 1; j < count; j++) {
            if (numbers[j] < numbers[minIndex])
                minIndex = j;
        }
        if (minIndex != i) {
            int temp = numbers[i];
            numbers[i] = numbers[minIndex];
            numbers[minIndex] = temp;
        }
    }
}

void showNumbers(int numbers[], int count) {
    for (int i = 0; i < count; i++)
        cout << numbers[i] << "  ";
    cout << "\n";
}

int main() {
    int numbers[] = {64, 34, 25, 12, 22, 11, 90};
    int count = 7;
    cout << "Unsorted: "; showNumbers(numbers, count);
    selectionSort(numbers, count);
    cout << "Sorted:   "; showNumbers(numbers, count);
    return 0;
}