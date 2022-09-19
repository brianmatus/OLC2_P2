#include <stdio.h>
#include <math.h>
double HEAP[40];
double STACK[20];
double P;
double H;

double t0,t1,t2,t3,t4,t5,t6,t7;


int main(){
P = 10;
H = 15;
//-------------------------------Declaration of y-------------------------------
t0 = 5 * 2;
t1 = 24 + t0;
t2 = 4 * 4;
t3 = t1 - t2;
t4 = P + 0;
STACK[(int)t4] = t3;
//-------------------------------Array Assignment of x-------------------------------
t5 = P + 1;
STACK[(int)t5] = H;
HEAP[(int)H] = 1;
H = H + 1;
HEAP[(int)H] = 2;
H = H + 1;
HEAP[(int)H] = 3;
H = H + 1;
HEAP[(int)H] = 4;
H = H + 1;
HEAP[(int)H] = 5;
H = H + 1;
HEAP[(int)H] = 6;
H = H + 1;
//-------------------------------Declaration of a-------------------------------
//-----String: ola xd-----
t6 = H  ;
HEAP[(int)H] = 111;
H = H + 1;
HEAP[(int)H] = 108;
H = H + 1;
HEAP[(int)H] = 97;
H = H + 1;
HEAP[(int)H] = 32;
H = H + 1;
HEAP[(int)H] = 120;
H = H + 1;
HEAP[(int)H] = 100;
H = H + 1;
HEAP[(int)H] = -1;
t7 = P + 2;
STACK[(int)t7] = t6;
printf("Final H:%f\n", H);
printf("Final P:%f\n", P);
printf("STACK:\n[\n");
int i;
for(i = 0; i < sizeof(STACK) / sizeof(double); i++){
printf("%i : %.2f\n", i, STACK[i]);
}
printf("]\n");
printf("HEAP:\n[\n");
for(i = 0; i < sizeof(HEAP) / sizeof(double); i++){
printf("%i : %.2f\n", i, HEAP[i]);
}
printf("]\n");
return 0;
}

