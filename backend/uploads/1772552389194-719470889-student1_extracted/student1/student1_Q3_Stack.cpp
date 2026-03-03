// Student: Ali Hassan | Q3: Stack Using Array
#include <iostream>
using namespace std;

#define MAX 100

class Stack {
    int arr[MAX];
    int top;
public:
    Stack() : top(-1) {}

    bool push(int val) {
        if (top >= MAX - 1) {
            cout << "Stack overflow!" << endl;
            return false;
        }
        arr[++top] = val;
        return true;
    }

    int pop() {
        if (top < 0) {
            cout << "Stack underflow!" << endl;
            return -1;
        }
        return arr[top--];
    }

    int peek() {
        if (top < 0) {
            cout << "Stack is empty!" << endl;
            return -1;
        }
        return arr[top];
    }

    bool isEmpty() { return top < 0; }
    bool isFull()  { return top >= MAX - 1; }
    int  size()    { return top + 1; }

    void display() {
        if (isEmpty()) { cout << "Stack is empty" << endl; return; }
        cout << "Stack (top->bottom): ";
        for (int i = top; i >= 0; i--)
            cout << arr[i] << " ";
        cout << endl;
    }
};

int main() {
    Stack s;
    s.push(10); s.push(20); s.push(30); s.push(40);
    cout << "After pushing 10,20,30,40:" << endl;
    s.display();
    cout << "Peek: " << s.peek() << endl;
    cout << "Pop: "  << s.pop()  << endl;
    cout << "Pop: "  << s.pop()  << endl;
    cout << "After two pops:" << endl;
    s.display();
    cout << "Size: " << s.size() << endl;
    return 0;
}