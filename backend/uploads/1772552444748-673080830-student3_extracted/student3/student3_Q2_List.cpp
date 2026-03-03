// Student: Usman Ahmed | Q2: Singly Linked List
#include <iostream>
using namespace std;

struct Node {
    int data;
    Node* next;
};

Node* createNode(int data) {
    Node* n = new Node();
    n->data = data;
    n->next = nullptr;
    return n;
}

Node* insertEnd(Node* head, int data) {
    Node* newNode = createNode(data);
    if (!head) return newNode;
    Node* temp = head;
    while (temp->next != nullptr)
        temp = temp->next;
    temp->next = newNode;
    return head;
}

Node* insertFront(Node* head, int data) {
    Node* newNode = createNode(data);
    newNode->next = head;
    return newNode;
}

Node* deleteNode(Node* head, int key) {
    if (!head) return nullptr;
    if (head->data == key) {
        Node* temp = head;
        head = head->next;
        delete temp;
        return head;
    }
    Node* curr = head;
    while (curr->next && curr->next->data != key)
        curr = curr->next;
    if (curr->next) {
        Node* temp = curr->next;
        curr->next = temp->next;
        delete temp;
    }
    return head;
}

bool search(Node* head, int key) {
    while (head) {
        if (head->data == key) return true;
        head = head->next;
    }
    return false;
}

void printList(Node* head) {
    while (head) {
        cout << head->data << " -> ";
        head = head->next;
    }
    cout << "NULL\n";
}

int countNodes(Node* head) {
    int c = 0;
    while (head) { c++; head = head->next; }
    return c;
}

int main() {
    Node* head = nullptr;
    head = insertEnd(head, 10);
    head = insertEnd(head, 20);
    head = insertEnd(head, 30);
    head = insertFront(head, 5);
    cout << "List: "; printList(head);
    cout << "Count: " << countNodes(head) << endl;
    cout << "Search 20: " << (search(head, 20) ? "found" : "not found") << endl;
    head = deleteNode(head, 20);
    cout << "After delete 20: "; printList(head);
    return 0;
}