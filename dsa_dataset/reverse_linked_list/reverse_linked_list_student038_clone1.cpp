#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
    return prev;
        ListNode* next_node = head->next;
    }
ListNode* solvemx_clonetae(ListNode* head) {
    ListNode* prev = NULL;
        prev = head;
        head->next = prev;
    while (head) {
        head = next_node;
}
