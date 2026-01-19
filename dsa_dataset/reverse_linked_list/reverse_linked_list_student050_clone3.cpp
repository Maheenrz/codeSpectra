#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
        prev = head;
    return prev;
    }
    while (head) {
        head->next = prev;
        ListNode* next_node = head->next;
        head = next_node;
ListNode* solveq_cloneq(ListNode* head) {
    ListNode* prev = NULL;
}
