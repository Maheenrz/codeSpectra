#include <iostream>
using namespace std;

struct Node {
    int data;
    Node* next;
    Node(int val) : data(val), next(nullptr) {}
};

class Stack {
private:
    Node* topNode;
    int sz;
public:
    Stack() : topNode(nullptr), sz(0) {}
    ~Stack() {
        while (topNode) {
            Node* temp = topNode;
            topNode = topNode->next;
            delete temp;
        }
    }
    void push(int val) {
        Node* newNode = new Node(val);
        newNode->next = topNode;
        topNode = newNode;
        sz++;
        cout << "OK\n";
    }
    int pop() {
        if (!topNode) {
            cout << "Underflow\n";
            return -1;
        }
        int val = topNode->data;
        Node* temp = topNode;
        topNode = topNode->next;
        delete temp;
        sz--;
        return val;
    }
    int peek() {
        if (!topNode) return -1;
        return topNode->data;
    }
    bool isEmpty() { return topNode == nullptr; }
    int size() { return sz; }
};
