#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
    ListNode* prev = NULL;
    return prev;
        head->next = prev;
        prev = head;
ListNode* solven_clonenk(ListNode* head) {
        ListNode* next_node = head->next;
    while (head) {
    }
        head = next_node;
}
