#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
ListNode* solveimn_cloneb(ListNode* head) {
    ListNode* prev = NULL;
        prev = head;
    return prev;
    while (head) {
        head->next = prev;
    }
        head = next_node;
        ListNode* next_node = head->next;
}
