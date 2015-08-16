#include <SoftwareSerial.h>
#include <SPI.h>
#define pinMOSI 11
#define PDB_COMMAND_WRITE 1

SoftwareSerial softSerial(5, 6); // RX, TX

int c = 0;

void setup() {
  Serial.begin(9600);
  softSerial.begin(9600);

  SPI.begin();
  SPI.setBitOrder(MSBFIRST);
  SPI.setClockDivider(SPI_CLOCK_DIV2);  // Need 8 MHz.  So use DIV2 on a 16 MHz board.s

  pinMode(13, OUTPUT);
  digitalWrite(13, c%2);
}

byte high;
byte low;

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

byte* banks = (byte*) calloc(2, sizeof(byte));

void loop() {

  /* Check for new commands */
  if (softSerial.available() > 2) {
    byte board = softSerial.read();
    byte bank = softSerial.read();
    byte value = softSerial.read();
    Serial.print("< ");
    Serial.print(board, HEX);
    Serial.print(" ");
    Serial.print(bank, HEX);
    Serial.print(" ");
    Serial.println(value, HEX);
    c++;
    digitalWrite(13, c%2);

    /* Multiple boards are not yet supported */
    if(board != 0) {
      Serial.print("ERROR, board != 0");
    } else if(bank > 1) {
      Serial.print("ERROR, bank > 1");
    } else {
      banks[bank] = value;
    }
  }

  /* Send commands to powerdriver */
  sendPDBCommand(0, PDB_COMMAND_WRITE, 0, banks[0]);  // Write data to bank 0
  sendPDBCommand(0, PDB_COMMAND_WRITE, 1, banks[1]); // Write inverted data to bank 1

}
