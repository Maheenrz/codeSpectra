#include <iostream>
#include <list>
using namespace std;

class Queue {
private:
    list<int> lst;
public:
    void enqueue(int val) {
        lst.push_back(val);
        cout << "OK\n";
    }
    int dequeue() {
        if (lst.empty()) {
            cout << "Queue empty\n";
            return -1;
        }
        int val = lst.front();
        lst.pop_front();
        return val;
    }
    int front() {
        if (lst.empty()) return -1;
        return lst.front();
    }
    bool isEmpty() { return lst.empty(); }
    int size() { return lst.size(); }
};
