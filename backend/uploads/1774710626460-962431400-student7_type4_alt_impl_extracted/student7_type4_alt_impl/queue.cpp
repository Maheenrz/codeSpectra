#include <iostream>
using namespace std;

struct Node {
    int data;
    Node* next;
    Node(int val) : data(val), next(nullptr) {}
};

class Queue {
private:
    Node* head;
    Node* tail;
    int cnt;
public:
    Queue() : head(nullptr), tail(nullptr), cnt(0) {}
    ~Queue() {
        while (head) {
            Node* tmp = head;
            head = head->next;
            delete tmp;
        }
    }
    void enqueue(int val) {
        Node* newNode = new Node(val);
        if (tail) tail->next = newNode;
        else head = newNode;
        tail = newNode;
        cnt++;
        cout << "OK\n";
    }
    int dequeue() {
        if (!head) {
            cout << "Empty\n";
            return -1;
        }
        int val = head->data;
        Node* tmp = head;
        head = head->next;
        if (!head) tail = nullptr;
        delete tmp;
        cnt--;
        return val;
    }
    int front() {
        if (!head) return -1;
        return head->data;
    }
    bool isEmpty() { return head == nullptr; }
    int size() { return cnt; }
};
