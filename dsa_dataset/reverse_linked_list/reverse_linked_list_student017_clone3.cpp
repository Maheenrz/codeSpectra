#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
        prev = head;
        ListNode* next_node = head->next;
    }
ListNode* solvek_clonep(ListNode* head) {
        head->next = prev;
    return prev;
    ListNode* prev = NULL;
    while (head) {
        head = next_node;
}
