// Student: Sara Khan | Q2: Singly Linked List
#include <iostream>
using namespace std;

struct Element {
    int value;
    Element* ptr;
    Element(int v) : value(v), ptr(nullptr) {}
};

class SinglyList {
    Element* start;
public:
    SinglyList() : start(nullptr) {}

    void appendNode(int v) {
        Element* fresh = new Element(v);
        if (!start) { start = fresh; return; }
        Element* cur = start;
        while (cur->ptr) cur = cur->ptr;
        cur->ptr = fresh;
    }

    void prependNode(int v) {
        Element* fresh = new Element(v);
        fresh->ptr = start;
        start = fresh;
    }

    void removeNode(int v) {
        if (!start) return;
        if (start->value == v) {
            Element* old = start;
            start = start->ptr;
            delete old;
            return;
        }
        Element* cur = start;
        while (cur->ptr && cur->ptr->value != v)
            cur = cur->ptr;
        if (cur->ptr) {
            Element* old = cur->ptr;
            cur->ptr = old->ptr;
            delete old;
        }
    }

    void show() {
        Element* cur = start;
        while (cur) {
            cout << cur->value << " -> ";
            cur = cur->ptr;
        }
        cout << "NULL" << endl;
    }

    int size() {
        int cnt = 0;
        Element* cur = start;
        while (cur) { cnt++; cur = cur->ptr; }
        return cnt;
    }
};

int main() {
    SinglyList list;
    list.appendNode(10);
    list.appendNode(20);
    list.appendNode(30);
    list.prependNode(5);
    cout << "List: "; list.show();
    cout << "Size: " << list.size() << endl;
    list.removeNode(20);
    cout << "After removing 20: "; list.show();
    return 0;
}