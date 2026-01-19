#include <iostream>
void push(int v) {
    extern int stack[], top, n;
    if (!(top < n - 1)) {
        std::cout << "Overflow";
        return;
    }
    stack[++top] = v;
}