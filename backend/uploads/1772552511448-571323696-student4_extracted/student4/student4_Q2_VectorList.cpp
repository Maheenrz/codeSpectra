// Student: Fatima Malik | Q2: Linked List using vector
#include <iostream>
#include <vector>
using namespace std;

class SimpleList {
    vector<int> items;
public:
    void insertBack(int val)  { items.push_back(val); }
    void insertFront(int val) { items.insert(items.begin(), val); }

    void remove(int val) {
        for (auto it = items.begin(); it != items.end(); ++it) {
            if (*it == val) { items.erase(it); return; }
        }
    }

    void display() {
        for (int i = 0; i < (int)items.size(); i++)
            cout << items[i] << (i + 1 < (int)items.size() ? " -> " : "");
        cout << " -> NULL\n";
    }

    int length() { return (int)items.size(); }
};

int main() {
    SimpleList list;
    list.insertBack(10);
    list.insertBack(20);
    list.insertBack(30);
    list.insertFront(5);
    cout << "List: "; list.display();
    cout << "Length: " << list.length() << endl;
    list.remove(20);
    cout << "After removing 20: "; list.display();
    return 0;
}