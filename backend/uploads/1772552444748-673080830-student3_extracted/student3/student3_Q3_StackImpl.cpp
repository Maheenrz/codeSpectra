// Student: Usman Ahmed | Q3: Stack Using Array (procedural style)
#include <iostream>
using namespace std;

const int STACK_SIZE = 100;

struct Stack {
    int data[STACK_SIZE];
    int top;
};

void initStack(Stack &s) {
    s.top = -1;
}

bool stackFull(Stack &s)  { return s.top >= STACK_SIZE - 1; }
bool stackEmpty(Stack &s) { return s.top == -1; }

void push(Stack &s, int value) {
    if (stackFull(s)) {
        cout << "[ERROR] Stack Overflow\n";
        return;
    }
    s.data[++s.top] = value;
    cout << "Pushed: " << value << "\n";
}

int pop(Stack &s) {
    if (stackEmpty(s)) {
        cout << "[ERROR] Stack Underflow\n";
        return -1;
    }
    return s.data[s.top--];
}

int peek(Stack &s) {
    if (stackEmpty(s)) return -1;
    return s.data[s.top];
}

int getSize(Stack &s) { return s.top + 1; }

void display(Stack &s) {
    if (stackEmpty(s)) { cout << "Empty stack\n"; return; }
    cout << "Top -> ";
    for (int i = s.top; i >= 0; i--)
        cout << s.data[i] << " ";
    cout << "<- Bottom\n";
}

int main() {
    Stack s;
    initStack(s);
    push(s, 10); push(s, 20); push(s, 30); push(s, 40);
    display(s);
    cout << "Peek: " << peek(s) << "\n";
    cout << "Popped: " << pop(s) << "\n";
    cout << "Popped: " << pop(s) << "\n";
    display(s);
    cout << "Current size: " << getSize(s) << "\n";
    return 0;
}