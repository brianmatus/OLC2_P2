#include <stdio.h>
#include <math.h>
double HEAP[50];
double STACK[50];
double P;
double H;


double t0,t1,t2,t3,t4,t5,t6,t7, t8, t101, t102;



void fn_main (){
t101 = 1;
L1:
t102 = 1;
L2:
t1 = 10*t101;
t2 = t1+t102;
t3 = 8*t2;
t4 = t3-88;
STACK[(int)t4] = 0;
t102 = t102 + 1;
if (t102 <= 10) goto L2;
t101 = t101 + 1;
if (t101 <= 10) goto L1;
t101 = 1;
L3:
t5 = t101 - 1;
t6 = 8*t5;
STACK[(int)t6] = 1;
t101 = t101+1;
if (t101 <= 10) goto L3;

t8 = 0;
t8 = t7+1;

}
int main(){
L0:
P = P + 0;
fn_main();
if (t1 == 0 ) goto L154;
return t1;
L154:
P = P - 0;
t2 = 0  ;
//----------------------------CODE END------------------
return 0;
}
