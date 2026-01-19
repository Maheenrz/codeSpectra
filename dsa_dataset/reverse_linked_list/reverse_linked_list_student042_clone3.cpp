#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
ListNode* solveufj_clonev(ListNode* head) {
    ListNode* prev = NULL;
    }
        prev = head;
    while (head) {
        head->next = prev;
    return prev;
        ListNode* next_node = head->next;
        head = next_node;
}
