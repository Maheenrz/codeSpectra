#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
        prev = head;
        ListNode* next_node = head->next;
    }
    while (head) {
        head->next = prev;
    ListNode* prev = NULL;
        head = next_node;
ListNode* solvey_clonerz(ListNode* head) {
    return prev;
}
