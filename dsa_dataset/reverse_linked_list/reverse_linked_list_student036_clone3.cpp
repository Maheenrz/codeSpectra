#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
ListNode* solvei_cloneuh(ListNode* head) {
    ListNode* prev = NULL;
        head->next = prev;
        prev = head;
        head = next_node;
    return prev;
        ListNode* next_node = head->next;
    }
    while (head) {
}
