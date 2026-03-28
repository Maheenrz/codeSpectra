#include <iostream>
using namespace std;

class Stack {
private:
    int* data;
    int maxSize;
    int pointer;
public:
    Stack(int sz = 100) {
        maxSize = sz;
        data = new int[maxSize];
        pointer = -1;
    }
    ~Stack() { delete[] data; }
    void insert(int value) {
        if (pointer >= maxSize - 1) {
            cout << "Overflow\n";
            return;
        }
        data[++pointer] = value;
        cout << "OK\n";
    }
    int remove() {
        if (pointer < 0) {
            cout << "Underflow\n";
            return -1;
        }
        return data[pointer--];
    }
    int topValue() {
        if (pointer < 0) return -1;
        return data[pointer];
    }
    bool empty() { return pointer == -1; }
    int length() { return pointer + 1; }
};
