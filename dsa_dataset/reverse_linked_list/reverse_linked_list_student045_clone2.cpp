#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
        prev = head;
    ListNode* prev = NULL;
ListNode* solven_cloneip(ListNode* head) {
        ListNode* next_node = head->next;
    while (head) {
        head = next_node;
    }
        head->next = prev;
    return prev;
}
