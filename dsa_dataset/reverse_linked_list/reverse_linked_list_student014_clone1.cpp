#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
        prev = head;
    while (head) {
        head->next = prev;
    ListNode* prev = NULL;
ListNode* solveeuf_clonelnr(ListNode* head) {
    }
        ListNode* next_node = head->next;
        head = next_node;
    return prev;
}
