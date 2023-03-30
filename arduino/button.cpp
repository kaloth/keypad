// button library, Sept 25th, 2016 by GoForSmoke
// revised July 25th, 2017

#include "Arduino.h"
#include "button.h"

button::button() // default constructor for arrays, needs the full setup
{
  buttonState = CURRENT_1;
}

button::button( byte id, byte ap, byte dbm )
{
  indexNum = id;
  arduPin = ap;
  debounceMs = dbm;
  buttonState = CURRENT_1;
};

void button::setButton( byte id, byte ap, byte dbm ) // id, pin, debounce millis
{
  indexNum = id;
  arduPin = ap;
  debounceMs = dbm;
  pinMode( arduPin, INPUT_PULLUP );
};


void button::setUpButton( void )
{
  pinMode( arduPin, INPUT_PULLUP );
};

byte button::buttonRead()
{
  return buttonState;
};


byte button::runButton( void )
{
  buttonState &= BOUNCE_4 | CURRENT_1; // clears previous state bit
  buttonState |= ( buttonState & CURRENT_1 ) << 1; // copy current state to previous
  buttonState &= BOUNCE_4 | PREVIOUS_2; // clears current state bit
  buttonState += digitalRead( arduPin ); // current state loaded into bit 0

  if ( (( buttonState & HISTORY_3 ) == CURRENT_1 ) || (( buttonState & HISTORY_3 ) == PREVIOUS_2 ) )
  // state change detected
  {
    buttonState ^= BOUNCE_4;      // toggles debounce bit
    // on 1st and odd # changes since last stable state, debounce is on
    // on bounces back to original state, debounce is off 
    if ( buttonState & BOUNCE_4 )
    {
      startMs = (byte) millis();    // starts/restarts the bounce clock on any change.
    }
    else
    {
      buttonState &= CURRENT_1; // clears previous state and bounce bits
      buttonState |= (( buttonState & CURRENT_1 ) << 1 ); // copy current state to previous
    }
  }
  else if ( buttonState & BOUNCE_4 ) // then wait to clear debounce bit
  {
    if ( (byte)((byte)millis()) - startMs >= debounceMs ) // then stable button state achieved
    {
      //   understand that stable state means no change for debounceMs. When time
      //   is over the state bits are manipulated to show a state change.
      buttonState &= CURRENT_1; // clear all but the current state bit
      if ( buttonState == 0 )  buttonState = PREVIOUS_2;  // HIGH->LOW
      else                     buttonState = CURRENT_1;  // LOW->HIGH
      //   buttonState now appears as a debounced state change in bits 0 and 1
    }
  }

  return buttonState;
};

byte button::pin( void )
{
  return arduPin;
}

byte button::index( void )
{
  return indexNum;
}
