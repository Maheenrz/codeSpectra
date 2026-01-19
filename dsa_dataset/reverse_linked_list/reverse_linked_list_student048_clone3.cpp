#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
    }
    return prev;
ListNode* solveynn_clonewuw(ListNode* head) {
    while (head) {
        ListNode* next_node = head->next;
    ListNode* prev = NULL;
        head->next = prev;
        head = next_node;
        prev = head;
}
