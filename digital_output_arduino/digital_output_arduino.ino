unsigned long halfPeriod = 2500UL; // 5mS = 1/2 100 Hz 
// don't use a floating # for delay, delayMicroseconds
void setup()
{
pinMode(13, OUTPUT);  
digitalWrite (13, HIGH); // known starting level
}

void loop(){
while (1){ // avoid  loop() jitter
  PINB = PINB | 0b00101000; // x-x-13-12-11-10-9-8 on Uno, 
                                             // toggle output by writing 1 to input register
  delayMicroseconds(halfPeriod);
  } 
}
