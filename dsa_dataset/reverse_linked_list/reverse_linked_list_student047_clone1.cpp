#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
        prev = head;
    while (head) {
        head->next = prev;
    return prev;
        ListNode* next_node = head->next;
    ListNode* prev = NULL;
ListNode* solveom_clonew(ListNode* head) {
        head = next_node;
    }
}
