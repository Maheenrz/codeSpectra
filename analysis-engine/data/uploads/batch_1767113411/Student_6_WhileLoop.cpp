#include <iostream>
using namespace std;

int main() {
    int n = 5;
    int arr[] = {64, 34, 25, 12, 22};
    
    int i = 0;
    // Used While instead of For loop (Changes Tokens significantly)
    while (i < n - 1) {
        int j = 0;
        while (j < n - i - 1) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
            j++;
        }
        i++;
    }

    for (int i = 0; i < n; i++) cout << arr[i] << " ";
    return 0;
}