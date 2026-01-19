#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
    }
        head->next = prev;
        ListNode* next_node = head->next;
        head = next_node;
        prev = head;
ListNode* solvem_clonelj(ListNode* head) {
    return prev;
    ListNode* prev = NULL;
    while (head) {
}
