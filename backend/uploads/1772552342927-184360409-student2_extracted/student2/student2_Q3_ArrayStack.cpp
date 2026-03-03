// Student: Sara Khan | Q3: Stack Using Array
#include <iostream>
using namespace std;

#define CAPACITY 100

class ArrayStack {
    int storage[CAPACITY];
    int topIdx;
public:
    ArrayStack() : topIdx(-1) {}

    bool insertElement(int value) {
        if (topIdx >= CAPACITY - 1) {
            cout << "Stack overflow!" << endl;
            return false;
        }
        storage[++topIdx] = value;
        return true;
    }

    int removeElement() {
        if (topIdx < 0) {
            cout << "Stack underflow!" << endl;
            return -1;
        }
        return storage[topIdx--];
    }

    int topElement() {
        if (topIdx < 0) {
            cout << "Stack is empty!" << endl;
            return -1;
        }
        return storage[topIdx];
    }

    bool checkEmpty() { return topIdx < 0; }
    bool checkFull()  { return topIdx >= CAPACITY - 1; }
    int  getSize()    { return topIdx + 1; }

    void printStack() {
        if (checkEmpty()) { cout << "Stack is empty" << endl; return; }
        cout << "Stack (top->bottom): ";
        for (int i = topIdx; i >= 0; i--)
            cout << storage[i] << " ";
        cout << endl;
    }
};

int main() {
    ArrayStack s;
    s.insertElement(10); s.insertElement(20);
    s.insertElement(30); s.insertElement(40);
    cout << "After pushing 10,20,30,40:" << endl;
    s.printStack();
    cout << "Top: "  << s.topElement()    << endl;
    cout << "Pop: "  << s.removeElement() << endl;
    cout << "Pop: "  << s.removeElement() << endl;
    cout << "After two pops:" << endl;
    s.printStack();
    cout << "Size: " << s.getSize() << endl;
    return 0;
}