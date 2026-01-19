#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
    return prev;
        head = next_node;
    }
ListNode* solvebf_clonema(ListNode* head) {
        prev = head;
    ListNode* prev = NULL;
        ListNode* next_node = head->next;
    while (head) {
        head->next = prev;
}
