
/*
  button.h for public domain use by GoForSmoke May 29 2015
  Revised Sept 2016  
  To use:
  make a buttonclass object in your sketch
  run that object every time through loop(), it is quickly done
  when you want to know the status of the button, you read the object
  it returns state;  bit 0 = current, bit 1 = previous, bit 2 = bounce
*/

// button library, Sept 25th, 2016 by GoForSmoke
// revised July 25th, 2017

#ifndef button_h
#define button_h

#include "Arduino.h"

#define CURRENT_1 1
#define PREVIOUS_2 2
#define HISTORY_3 3
#define BOUNCE_4 4

class button
{
private:
  byte indexNum;
  byte arduPin;
  byte buttonState; // bit 0 = current, bit 1 = previous, bit 2 = bounce
  byte startMs;
  byte debounceMs; 

public:
  button(); // default constructor
  void setButton( byte, byte, byte ); // id, pin, debounce millis
  button( byte, byte, byte ); // id, pin, debounce millis
  void setUpButton( void );
  byte runButton( void ); // returns buttonState as below
  // buttonState: bit 0 = current, bit 1 = previous, bit 2 = bounce
  byte buttonRead();  // returns buttonState as above
  byte pin();
  byte index();
};

#endif
