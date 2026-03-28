#include <iostream>
using namespace std;

class Queue {
private:
    int* arr;
    int front;
    int rear;
    int capacity;
    int count;
public:
    Queue(int cap = 100) {
        capacity = cap;
        arr = new int[capacity];
        front = 0;
        rear = -1;
        count = 0;
    }
    ~Queue() { delete[] arr; }
    void enqueue(int val) {
        if (count == capacity) {
            cout << "Queue Full\n";
            return;
        }
        rear = (rear + 1) % capacity;
        arr[rear] = val;
        count++;
        cout << "OK\n";
    }
    int dequeue() {
        if (count == 0) {
            cout << "Queue Empty\n";
            return -1;
        }
        int val = arr[front];
        front = (front + 1) % capacity;
        count--;
        return val;
    }
    int frontValue() {
        if (count == 0) return -1;
        return arr[front];
    }
    bool isEmpty() { return count == 0; }
    int size() { return count; }
};
