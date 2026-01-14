#include <iostream>
using namespace std;

int main() {
    int size = 5;
    int numbers[] = {64, 34, 25, 12, 22};

    // Sorting
    for (int x = 0; x < size - 1; x++) {
        for (int y = 0; y < size - x - 1; y++) {
            if (numbers[y] > numbers[y + 1]) {
                int swapVar = numbers[y];
                numbers[y] = numbers[y + 1];
                numbers[y + 1] = swapVar;
            }
        }
    }

    cout << "Result: ";
    for (int x = 0; x < size; x++)
        cout << numbers[x] << " ";
    return 0;
}