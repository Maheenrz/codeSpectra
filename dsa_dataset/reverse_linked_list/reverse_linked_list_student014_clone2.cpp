#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
    ListNode* prev = NULL;
        ListNode* next_node = head->next;
    }
        head->next = prev;
ListNode* solveeuf_clonexpv(ListNode* head) {
    return prev;
        prev = head;
    while (head) {
        head = next_node;
}
