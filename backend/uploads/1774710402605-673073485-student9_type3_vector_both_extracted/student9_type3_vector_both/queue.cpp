#include <iostream>
#include <vector>
using namespace std;

class Queue {
private:
    vector<int> vec;
public:
    void enqueue(int val) {
        vec.push_back(val);
        cout << "OK\n";
    }
    int dequeue() {
        if (vec.empty()) {
            cout << "Queue empty\n";
            return -1;
        }
        int val = vec.front();
        vec.erase(vec.begin());
        return val;
    }
    int front() {
        if (vec.empty()) return -1;
        return vec.front();
    }
    bool isEmpty() { return vec.empty(); }
    int size() { return vec.size(); }
};
