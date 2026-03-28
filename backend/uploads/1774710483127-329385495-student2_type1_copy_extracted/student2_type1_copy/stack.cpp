#include <iostream>
using namespace std;

class Stack {
private:
    int* arr;
    int capacity;
    int top;
public:
    Stack(int size = 100) {
        capacity = size;
        arr = new int[capacity];
        top = -1;
    }
    ~Stack() { delete[] arr; }
    void push(int val) {
        if (top >= capacity - 1) {
            cout << "Stack Overflow\n";
            return;
        }
        arr[++top] = val;
        cout << "OK\n";
    }
    int pop() {
        if (top < 0) {
            cout << "Stack Underflow\n";
            return -1;
        }
        return arr[top--];
    }
    int peek() {
        if (top < 0) return -1;
        return arr[top];
    }
    bool isEmpty() { return top == -1; }
    int size() { return top + 1; }
};
