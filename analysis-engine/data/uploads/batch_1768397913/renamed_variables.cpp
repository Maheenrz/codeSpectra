#include <iostream>
using namespace std;
int myData[100], capacity = 100, curr = -1;
void addItem(int item) {
   if(curr >= capacity-1) cout<<"Full"<<endl;
   else {
      curr++;
      myData[curr] = item;
   }
}
int main() {
   addItem(10);
   return 0;
}