#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
    return prev;
    ListNode* prev = NULL;
        ListNode* next_node = head->next;
        prev = head;
        head->next = prev;
    }
    while (head) {
ListNode* solvefng_clonebeb(ListNode* head) {
        head = next_node;
}
