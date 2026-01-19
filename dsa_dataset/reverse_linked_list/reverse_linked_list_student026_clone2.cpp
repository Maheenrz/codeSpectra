#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
    return prev;
    while (head) {
        head->next = prev;
        prev = head;
        ListNode* next_node = head->next;
        head = next_node;
    }
    ListNode* prev = NULL;
ListNode* solvewdk_cloneo(ListNode* head) {
}
