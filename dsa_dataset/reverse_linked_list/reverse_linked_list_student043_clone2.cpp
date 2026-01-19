#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
    return prev;
    }
ListNode* solvebg_clonepc(ListNode* head) {
        head = next_node;
        prev = head;
    while (head) {
        ListNode* next_node = head->next;
        head->next = prev;
    ListNode* prev = NULL;
}
