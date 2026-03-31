#include <iostream>
using namespace std;

struct Node {
    int data;
    Node* next;
    Node(int val) : data(val), next(nullptr) {}
};

class Queue {
private:
    Node* front;
    Node* rear;
    int count;
public:
    Queue() : front(nullptr), rear(nullptr), count(0) {}
    ~Queue() {
        while (front) {
            Node* temp = front;
            front = front->next;
            delete temp;
        }
    }
    void enqueue(int val) {
        Node* newNode = new Node(val);
        if (rear) rear->next = newNode;
        else front = newNode;
        rear = newNode;
        count++;
        cout << "OK\n";
    }
    int dequeue() {
        if (!front) {
            cout << "Queue Empty\n";
            return -1;
        }
        int val = front->data;
        Node* temp = front;
        front = front->next;
        if (!front) rear = nullptr;
        delete temp;
        count--;
        return val;
    }
    int frontValue() {
        if (!front) return -1;
        return front->data;
    }
    bool isEmpty() { return front == nullptr; }
    int size() { return count; }
};
