#include <iostream>
using namespace std;
int stack[100], n = 100, top = -1;
void push(int val) {
   if(top >= n-1) cout<<"Stack Overflow"<<endl;
   else {
      top++;
      stack[top] = val;
   }
}
int main() {
   push(10);
   return 0;
}