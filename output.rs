#include <stdio.h>
#include <math.h>
double HEAP[40];
double STACK[20];
double P;
double H;

double t0;


int main(){
P = 10;
H = 15;
//-------------------------------Array Assignment of y-------------------------------
t0 = P + 0;
STACK[(int)t0] = H;
HEAP[(int)H] = 1;
H = H + 1;
HEAP[(int)H] = 2;
H = H + 1;
HEAP[(int)H] = 3;
H = H + 1;
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

