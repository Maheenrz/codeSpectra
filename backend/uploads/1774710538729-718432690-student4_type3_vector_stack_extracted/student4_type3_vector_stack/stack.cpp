#include <iostream>
#include <vector>
using namespace std;

class Stack {
private:
    vector<int> data;
public:
    void push(int val) {
        data.push_back(val);
        cout << "OK\n";
    }
    int pop() {
        if (data.empty()) {
            cout << "Underflow\n";
            return -1;
        }
        int val = data.back();
        data.pop_back();
        return val;
    }
    int peek() {
        if (data.empty()) return -1;
        return data.back();
    }
    bool isEmpty() { return data.empty(); }
    int size() { return data.size(); }
};
