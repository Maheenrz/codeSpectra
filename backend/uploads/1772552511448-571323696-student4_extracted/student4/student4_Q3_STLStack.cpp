// Student: Fatima Malik | Q3: Stack using STL
#include <iostream>
#include <stack>
using namespace std;

void demonstrateStack() {
    stack<int> myStack;

    // Push elements
    int values[] = {10, 20, 30, 40};
    for (int v : values) {
        myStack.push(v);
        cout << "Pushed: " << v << "\n";
    }

    cout << "Stack size: " << myStack.size() << "\n";
    cout << "Top element: " << myStack.top() << "\n";

    // Pop two elements
    for (int i = 0; i < 2; i++) {
        cout << "Popped: " << myStack.top() << "\n";
        myStack.pop();
    }

    cout << "Size after pops: " << myStack.size() << "\n";

    // Display remaining (copy to temp)
    stack<int> temp = myStack;
    cout << "Remaining (top->bottom): ";
    while (!temp.empty()) {
        cout << temp.top() << " ";
        temp.pop();
    }
    cout << "\n";
}

int main() {
    demonstrateStack();
    return 0;
}