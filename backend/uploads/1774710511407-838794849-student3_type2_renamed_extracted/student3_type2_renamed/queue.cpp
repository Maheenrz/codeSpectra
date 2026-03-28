#include <iostream>
using namespace std;

struct Node {
    int value;
    Node* next;
    Node(int v) : value(v), next(nullptr) {}
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
    void add(int v) {
        Node* newNode = new Node(v);
        if (tail) tail->next = newNode;
        else head = newNode;
        tail = newNode;
        cnt++;
        cout << "OK\n";
    }
    int remove() {
        if (!head) {
            cout << "Empty\n";
            return -1;
        }
        int v = head->value;
        Node* tmp = head;
        head = head->next;
        if (!head) tail = nullptr;
        delete tmp;
        cnt--;
        return v;
    }
    int getFront() {
        if (!head) return -1;
        return head->value;
    }
    bool isEmpty() { return head == nullptr; }
    int getSize() { return cnt; }
};
