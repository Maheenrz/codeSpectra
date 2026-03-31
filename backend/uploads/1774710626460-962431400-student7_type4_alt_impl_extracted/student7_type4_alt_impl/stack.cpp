#include <iostream>
#include <deque>
using namespace std;

class Stack {
private:
    deque<int> dq;
public:
    void push(int val) {
        dq.push_back(val);
        cout << "OK\n";
    }
    int pop() {
        if (dq.empty()) {
            cout << "Empty stack\n";
            return -1;
        }
        int val = dq.back();
        dq.pop_back();
        return val;
    }
    int peek() {
        if (dq.empty()) return -1;
        return dq.back();
    }
    bool isEmpty() { return dq.empty(); }
    int size() { return dq.size(); }
};
