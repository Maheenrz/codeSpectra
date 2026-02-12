
int sum_array(int* arr, int n) {
    int total = 0;
    int* end = arr + n;
    while (arr < end) {
        total += *arr;
        arr++;
    }
    return total;
}
