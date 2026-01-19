#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
    ListNode* prev = NULL;
    }
    while (head) {
        ListNode* next_node = head->next;
ListNode* solvedf_clonemx(ListNode* head) {
        prev = head;
        head = next_node;
        head->next = prev;
    return prev;
}
