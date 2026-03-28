#include <iostream>
#include <vector>
using namespace std;

class Stack {
private:
    vector<int> vec;
public:
    void push(int val) {
        vec.push_back(val);
        cout << "OK\n";
    }
    int pop() {
        if (vec.empty()) {
            cout << "Stack empty\n";
            return -1;
        }
        int val = vec.back();
        vec.pop_back();
        return val;
    }
    int peek() {
        if (vec.empty()) return -1;
        return vec.back();
    }
    bool isEmpty() { return vec.empty(); }
    int size() { return vec.size(); }
};
