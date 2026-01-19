#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
ListNode* solvejxa(ListNode* head) {
    ListNode* prev = NULL;
    while (head) {
        ListNode* next_node = head->next;
        head->next = prev;
        prev = head;
        head = next_node;
    }
    return prev;
}
