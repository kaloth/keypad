#include <avr/io.h>
#include "button.h"

button *buttons[] = {
  new button( 0, A4, 5 ),
  new button( 1, A5, 5 ),
  new button( 2, 2, 5 ),
  new button( 3, 3, 5 ),
  new button( 4, 4, 5 ),
  new button( 5, 5, 5 ),
  new button( 6, 6, 5 ),
  new button( 7, 7, 5 ),
};
byte button_count = sizeof(buttons)/sizeof(button*);

byte lights[] = {
  9,
  10,
  11,
  12,
  13,
};
byte light_count = sizeof(lights)/sizeof(byte);
byte light_base_pin = lights[0];

void setup()
{
  Serial.begin( 115200 );
  Serial.setTimeout(250);
  Serial.print("\n\n\n\n0h\n");
  Serial.print( button_count );
  Serial.print("b\n" );
  Serial.print( light_count );
  Serial.print("l\n" );
  
  for (byte i = 0; i < button_count; i++)
  {
    buttons[i]->setUpButton();
  }
  
  for (byte i = 0; i < light_count; i++)
  {
    pinMode(lights[i], OUTPUT);
    digitalWrite(lights[i], HIGH);
    delay(250);
  }
  
  delay(1000);
  
  for (byte i = 0; i < light_count; i++)
  {
    digitalWrite(lights[i], LOW);   
  }
};

void processButton(button *btn)
{
  byte buttonState = btn->runButton();
  
  switch ( buttonState )
  {
    case CURRENT_1 :
    {
      Serial.print(btn->index());
      Serial.print("u\n");
      break;
    }
    case PREVIOUS_2 :
    {
      Serial.print(btn->index());
      Serial.print("d\n");
      break;
    }
  }
}

void loop()
{
  // process the button states..
  for (byte i = 0; i < button_count; i++)
  {
    processButton(buttons[i]);
  }
  
  // read light commands from serial..
  while (Serial.available() > 0)
  {
	  String data = Serial.readStringUntil('\n');
	  byte command = data[0];
	  byte value = data[1];
	  
	  //Serial.print("0i - ");
	  //Serial.print(data);
	  //Serial.print("\n");
	  
	  switch(command)
	  {
	  	case 'l':
	  	{
	  		value -= 48; // char 0 to decimal 0.
	  		if (value < light_count)
	  		{
	  			digitalWrite(lights[value], HIGH);
	  		}
	  		break;
	  	}
	  	case 'd':
	  	{
	  		value -= 48; // char 0 to decimal 0.
	  		if (value < light_count)
	  		{
	  			digitalWrite(lights[value], LOW);
	  		}
	  		break;
	  	}
	  }
  }
}
