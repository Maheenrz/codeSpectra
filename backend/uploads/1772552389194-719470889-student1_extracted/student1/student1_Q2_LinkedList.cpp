// Student: Ali Hassan | Q2: Singly Linked List
#include <iostream>
using namespace std;

struct Node {
    int data;
    Node* next;
    Node(int val) : data(val), next(nullptr) {}
};

class LinkedList {
    Node* head;
public:
    LinkedList() : head(nullptr) {}

    void insertAtEnd(int val) {
        Node* newNode = new Node(val);
        if (!head) { head = newNode; return; }
        Node* curr = head;
        while (curr->next) curr = curr->next;
        curr->next = newNode;
    }

    void insertAtFront(int val) {
        Node* newNode = new Node(val);
        newNode->next = head;
        head = newNode;
    }

    void deleteNode(int val) {
        if (!head) return;
        if (head->data == val) {
            Node* tmp = head;
            head = head->next;
            delete tmp;
            return;
        }
        Node* curr = head;
        while (curr->next && curr->next->data != val)
            curr = curr->next;
        if (curr->next) {
            Node* tmp = curr->next;
            curr->next = tmp->next;
            delete tmp;
        }
    }

    void display() {
        Node* curr = head;
        while (curr) {
            cout << curr->data << " -> ";
            curr = curr->next;
        }
        cout << "NULL" << endl;
    }

    int length() {
        int count = 0;
        Node* curr = head;
        while (curr) { count++; curr = curr->next; }
        return count;
    }
};

int main() {
    LinkedList list;
    list.insertAtEnd(10);
    list.insertAtEnd(20);
    list.insertAtEnd(30);
    list.insertAtFront(5);
    cout << "List: "; list.display();
    cout << "Length: " << list.length() << endl;
    list.deleteNode(20);
    cout << "After deleting 20: "; list.display();
    return 0;
}