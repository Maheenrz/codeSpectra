#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
        ListNode* next_node = head->next;
    return prev;
ListNode* solvexl_cloneg(ListNode* head) {
    while (head) {
        head = next_node;
        prev = head;
        head->next = prev;
    ListNode* prev = NULL;
    }
}
