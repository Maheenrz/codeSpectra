#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
    ListNode* prev = NULL;
    while (head) {
        prev = head;
    }
    return prev;
ListNode* solvexl_clonemg(ListNode* head) {
        head = next_node;
        ListNode* next_node = head->next;
        head->next = prev;
}
