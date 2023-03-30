# FinalFury Keypad v1.0

Thank you for choosing the FinalFury Keypad v1.0 "Flappy Switch Box" (tm). Our very first custom gaming peripheral.

## Python Script Setup
Install Python 3 from [here](https://www.python.org/downloads/). 

Next install the additional dependencies by running the following command.

    python -m pip install -r requirements.txt

## USB Serial Driver Installation

This keypad uses an Arduino Nano with a **CH340** USB Serial interface. Please unzip the included driver package "ELEGOO CH340 Driver 2022.09.29.zip" or alternatively download the latest from [Elegoo](https://www.elegoo.com/pages/download).

## Command Line Options

    usage: keypad.py [-h] -p COM_PORT [-s SETTINGS_FILE]
    
    optional arguments:
      -h, --help            show this help message and exit
      -p COM_PORT, --com_port COM_PORT
                            The com port name where your keypad is attached. (eg: COM3)
      -s SETTINGS_FILE, --settings_file SETTINGS_FILE
                            Path to your json settings file

## Which COM Port?

In order to determine which com port to use follow these steps on Windows 10..

 * Right click on the Windows button.
 * Choose 'Device Manager'.
 * Expand the 'Ports (COM & LPT)'.
 * Remember the port name listed next to 'USB-SERIAL CH340' in brackets.

# Settings File
The settings file allows you to customise the operation of you keypad. It's a simple json file describing a nested dictionary. The top level of the dictionary lists application binary names (eg: 'notepad.exe') with one reserved name of '\_default\_' which is used to specify settings that should be applied when no specific entry is available for the currently focused application.

Within each application dictionary you will then find a 'lightmap' and a 'keymap' entry. Within these you can specify custom behaviors for the lights and keys of your keypad that will be in operation whenever the named application is the currently focused window.

## Lightmap
The light map specifies a list of consecutively numbered lights in a dictionary with settings for each light described in a further nested dictionary of key:value pairs. By default lights only require one field 'type'.

The following table describes the available light types.

Name| Description| Additional Parameters
-------- | ----- | -----
always | Light is always on | 
never | Light is always off | 
pattern | Light is on/off over time according to a pattern of '#' and ' ' chars where each char represents 1/8th of a second. | **pattern**: <list of #s and spaces>
elite_dangerous_status | light state follows the value of an Elite Dangerous status flag modulated by a pattern. | **pattern**: <list of #s and spaces> **edstatus**: <Elite Dangerous status code, see reference>

## Keymap
The key map specifies settings for each of the switches and keys on your keypad. It has a similar layout to the lightmap. By default keys require three fields.

Name| Description
-------- | ----- 
type | The switch type. See table below
invert | Invert the key state transition events coming from the keypad. Up becomes down and down becomes up.
keypress | A string describing the keyboard event(s) that the key will trigger. These are as described [here](https://github.com/boppreh/keyboard). For example "ctrl+shift+m".

The following key types are available..

Name| Description| Additional Parameters
-------- | ----- | -----
default or hw_toggle| Switch state is taken raw from the switch HW | 
sw_toggle| Each press/release cycle of the switch will toggle the switch state | 
press_release_ud| Press and release events are triggered on all state transitions of the HW switch | 
press_release_u| Press and release events are triggered on transitions to the up state of the HW switch | 
press_release_d| Press and release events are triggered on transitions to the down state of the HW switch |  
elite_dangerous_autotoggle | Switch state is tracked like hw_toggle. Additionally Elite Dangerous status is tracked and kept in sync with the HW switch. Assumes that key-bindings in Elite Dangerous are set to match 'keypress' value | **edstatus**: <Elite Dangerous status code, see reference>

## Elite Dangerous Status Codes
The following table lists the currently known status codes that can be used along with the 'elite_dangerous_autotoggle' key type and the 'elite_dangerous_status' light type.
Name| Description | Light | Key
-------- | ----- | ----- | ----- 
0  | Docked (on a landing pad) | x | 
1  | Landed (on planet surface) | x | 
2  | Landing Gear Down | x | x
3  | Shields Up | x | 
4  | Supercruise | x | x
5  | FlightAssist Off | x | x
6  | Hardpoints Deployed | x | x
7  | In Wing | x |
8  | LightsOn | x | x
9  | Cargo Scoop Deployed | x | x
10 | Silent Running | x | x
11 | Scooping Fuel | x | 
12 | Srv Handbrake | x | x
13 | Srv using Turret view | x |
14 | Srv Turret retracted (close to ship) | x |
15 | Srv DriveAssist | x | x
16 | Fsd MassLocked | x |
17 | Fsd Charging | x |
18 | Fsd Cooldown | x |
19 | Low Fuel ( < 25% ) | x |
20 | Over Heating ( > 100% ) | x |
21 | Has Lat Long | x |
22 | IsInDanger | x |
23 | Being Interdicted | x |
24 | In MainShip | x |
25 | In Fighter | x |
26 | In SRV | x |
27 | Hud in Analysis mode | x |
28 | Night Vision | x | x
