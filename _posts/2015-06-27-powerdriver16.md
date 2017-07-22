---
layout: post
title:  "Powerdriver 16 master"
date:   2015-06-27 12:00:00
categories: raspberry powerdriver spi hardware
---

Today the powerdriver 16 master board (powerdriver) has arrived. This board will be used to
programmatically activate the coils in the game. Although I have not purchased
any coils yet I'll have a quick look on the device. In this post I'll explain a
bit on why I use this board, show what is in the box, and how to communicate
with it using an Arduino.

## Why the powerdriver?

* Programmatically enable/disable hardware devices.
* It has fuses!
* It has a watchdog!
* It has `flyback` diodes! "Each transistor circuit includes a flyback diode to
  eliminate voltage spikes on inductive loads, such as coils. It is therefore
  unnecessary to put diodes on coils activated by this board."
* Some feeling of safety: no power on electrical circuits that should not be
  activated.

## Unboxing!
The powerdriver does not come in a fancy box (who cares anyway?)
In the envelop there was exactly one powerdriver master and a ribbon cable.
I also ordered the required molex connectors.

## Controlling the unit with an Arduino

The powerdriver is a cool device that can be used to set and cut power on
the power-hungry devices in a pinball machine. There are at least two ways to
send instructions to the powerdriver.

* Using Pinballcontrollers.com [P-ROC](http://www.pinballcontrollers.com/index.php/products/p-roc) or [P3-ROC](http://www.pinballcontrollers.com/index.php/products/p3-roc):
  Pinballcontrollers is also the producer of the powerdriver. With this (rather
  expensive!) board one can send commands over USB to the P-ROC, and the P-ROC
  on its turn controls the powerdriver. (Or at least, that is how I understand
  it).

* Using [SPI](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus):
  SPI is a serial bus on which commands can be sent to the powerdriver.
  The powerdriver can be controlled by using a very simple protocol. Example
  code to use the powerdriver over SPI using an Arduino can be found [here](http://www.pinballcontrollers.com/index.php/products/driver-boards/driver-board-faq/83).

Since I don't want to spend a bunch of money on a P-ROC yet, I'll attempt to
control the powerdriver using the Arduino.

### The protocol in a nutshell

For more information please refer to the official [manual](http://www.pinballcontrollers.com/docs/Driver_Board_specs/Power-Driver-16_LLD.pdf).

The `PDB Protocol` sends a sequence of bytes to the board. It is defined as
follows:

    sendByte(board address, command, bank, databyte):

		Send byte 0: `Board Address`
		1-5 IDLE clock cycles

		Send byte 1: `Command` (0: READ or 1: WRITE)
		1-5 IDLE clock cycles

		Send byte 2: `Bank` (0: A or 1: B)
		1-5 IDLE clock cycles

		Send byte 3: higher nibble of databyte (databyte >> 4)
		1-5 IDLE clock cycles

		Send byte 4: lower nibble of databyte (databyte & 0x0F)
		>=10 IDLE clock cycles

, where `databyte` tells which devices on a bank should get power.
The documentation states that the SPI bus should be set at 8Mhz. Luckly this is supported by the Arduino.
(The Raspberry does not natively support this speed, but the SPI speed of the Raspberry can be set to 7.8Mhz. I may do some experiments in the 
future to check whether the Pi can be used as well!)


### Demo application

To validate the working of the powerdriver, I have set up a very small test environment.
In the test environment I connected a led to each output of a single bank.
By running the demo code leds will light up as if the leds are a [Cylon](http://en.battlestarwiki.org/wiki/Cylon_Centurion) eye,
as shown in the following clip:

![Leds turned on by the powerdriver]({{ site.baseurl }}/assets/images/powerdriver_leds.gif)


#### Wiring
An Arduino is used to communicate with the powerdriver over SPI.
The Arduino SPI output is 5V, and the powerdriver SPI input must be 3.3V.
A [level shifter]({{ site.baseurl }}/shoppinglist) is used to convert the 5V SPI signal to a 3.3V SPI signal.

* Arduino 5V in (USB cable)

* Arduino 5V out to Level shifter POWER HIGH in
* Arduino 3.3V out to level shifter POWER LOW in
* Arduino GND to level shifter GND HIGH
* Arduino  pin 11 (5V SPI out) to Level shifter HIGH in

* Level shifter LOW out (3.3V shifted SPI) to powerdriver J8 pin 1
* Level shifter GND LOW to powerdriver J8 pin 2

* 5V in/out to powerdriver J1 (powerboard power)
* 5V in/out from powerdriver J5 (SINK IN)
* 5V out powerdriver J3 (SINK OUT) to breadboard HIGH LINE

* For each pin *i* in each pin on BANK A (*i*: 1 t/m 8):
    * BREADBOARD HIGH LINE -> Resistor *i* -> LED *i* -> Pin *i* on BANK A (low)




#### Source code
{% highlight c %}

#include <SPI.h>
#define pinMOSI 11
#define PDB_COMMAND_WRITE 1



/* Initialise the SPI bus */
void setup() {
  SPI.begin();
  SPI.setBitOrder(MSBFIRST);
  SPI.setClockDivider(SPI_CLOCK_DIV2);  // Need 8 MHz.  So use DIV2 on a 16 MHz board.
}

/* Set the devices HIGH according to the bits in the data byte */
void sendPDBCommand(byte addr, byte command, byte bankAddr, byte data)
{
  high = (data >> 4) & 0xF;
  low = data & 0xF;
  
  // Turn off interrupts so the transfer doesn't get interrupted.
  noInterrupts();
  // Hardcode transfers to minimize IDLEs between transfers.
  // Using a for-loop adds 5 extra IDLEs between transfers.  
  SPI.transfer(addr);
  SPI.transfer(command); 
  SPI.transfer(bankAddr);
  SPI.transfer(high); 
  SPI.transfer(low);
  // Re-enable interrupts
  interrupts();
}

/*
   Loop parameters and loop code 
   In the data byte only one bit is set to HIGH, reprenting a
   single LED to be on. Each iteration, the active bit is moved 
   one place left- or rightwards.
   
   Example:
   run 1: 00000001
   run 2: 00000010  (applying data << 1)
   run 3: 00000100  (applying data << 1)
   (...)
   
*/
byte high;
byte low;
bool up = true;
byte data = 1;
void loop() {
    if(up) {
      data = data << 1; /* bit shift left */
    } else {
      data = data >> 1; /* bit shift right */
    }
  if(data == 1) {
    up = true;
  } else if(data == 0b10000000) {
    up = false;
  }
  byte board = 0;
  sendPDBCommand(board, PDB_COMMAND_WRITE, 0, data);  // Write data to bank 0
  delay(150);
}
{% endhighlight %}

*Disclaimer*: this is **not** the most compact form of writing this program. However by being a bit more explicit, I hope that it is better readable and understandable by novice programmers.

Some observations:

* Putting all upper or al lower bytes to high (sending 0x0F as high or low byte) causes
  some devices not to be activated. Possibly due to timing issues.

* The watchdog LED is always **on** unless the delay is set to 0.

* No explicit `1-5 IDLE clock cycles` in the Arduino sketch.
