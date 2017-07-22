import smbus

from .hwgamedevice import OutGameDevice, InGameDevice
from .hwcontroller import HWController


class Mcp23017(HWController):
    """
    MCP23017: 16 bit i/o extender. Can be used to control 16 GPIO devices
    per unit. Multiple units can be used by changing the address.

    Datasheet: http://ww1.microchip.com/downloads/en/DeviceDoc/21952b.pdf

    To use this hardware device most efficiently use a single bank for input
    only, or for output only (e.g. bank A input devices only, and bank B output
    defices only).


    # Pin layout
    Placed here for reference, not to replace the original documentation

                  ____   _____
    GPB0 <--> 01  |   \_/    |  28 <--> GPA7
    GPB1 <--> 02  |          |  27 <--> GPA6
    GPB2 <--> 03  |          |  26 <--> GPA5
    GPB3 <--> 04  |    M     |  25 <--> GPA4
    GPB4 <--> 05  |    C     |  24 <--> GPA3
    GPB5 <--> 06  |    P     |  23 <--> GPA2
    GPB6 <--> 07  |    2     |  22 <--> GPA1
    GPB7 <--> 08  |    3     |  21 <--> GPA0
     VDD <--> 09  |    0     |  20  --> INTA
     VSS  --> 10  |    1     |  19  --> INTB
      NC  --  11  |    7     |  18  --> RESET
     SCL  --> 12  |          |  17 <--  A2
     SDA <--> 13  |          |  16 <--  A1
      NC  --  14  |__________|  15 <--  A0


    Connections:
     GPB*: Bank B input/output, where * is the nth-LSB bit in the address mask
     GPA*: Bank A input/output,  "

     VDD: 3.3V in (5.5V should work as well)
     VSS: GND
     SCL: I2C clock
     SDA: I2C data
     RESET: 3.3V in (5.5V should work as well)
     A1,A1,A2: GND --> I2C address 0x20. Refer to datasheet for details.

    """

    # Device specific registers
    IODIRA = 0x00   # Pin direction (bank A)
    IODIRB = 0x01   # Pin direction (bank B)
    GPIOA = 0x12    # Register for inputs (bank A)
    GPIOB = 0x13    # Register for inputs (bank B)
    OLATA = 0x14    # Register for outputs (bank A)
    OLATB = 0x15    # Register for outputs (bank B)

    BANKA = 0x00    # Index in state variable :for this bank
    BANKB = 0x01

    def __init__(self, address):

        self.bus = smbus.SMBus(1)
        self._address = address

        # Dirty flag, if True the OUTPUT state of hardware has to be updated
        self._dirty = [False, False]

        # States that hold the active / inactive state for the output
        self._state = [0x00, 0x00]

        # Keep track of IO directions (bitmap, 1 means input)
        self._directions = [0x00, 0x00]

        # For bank A and B keep the input devices
        self._indevices = [[], []]

        # Keep all devices in a single list to return to the HWController
        self._devices = []

        # Initialise by setting all values as output and set to LOW
        self.bus.write_byte_data(self._address, self.IODIRA, 0x00)
        self.bus.write_byte_data(self._address, self.IODIRB, 0x00)
        self.sync()

    def getHwDevices(self):
        return self._devices

    def getOut(self, name, pin, bank):
        """Returns an output device object associated with the provided pin and
        bank.

        This method configures the Mcp23017 unit as well.
        @param name Name of the device
        @param pin  Pin on the bank
        @param bank Bank identifier (use Mcp23017.BANKA or Mcp23017.BANKB)
        """
        device = Mcp23017OutGameDevice(name, self, pin, bank)
        self._devices.append(device)
        return device

    def getIn(self, name, pin, bank, **kwargs):
        """Returns an input device object associated with the provided pin and
        bank.

        This method configures the Mcp23017 unit as well.
        @param name Name of the device
        @param pin  Pin on the bank
        @param bank Bank identifier (use Mcp23017.BANKA or Mcp23017.BANKB)
        """
        self._directions[bank] |= pin

        self.bus.write_byte_data(
            self._address, self.IODIRA, self._directions[self.BANKA])
        self.bus.write_byte_data(
            self._address, self.IODIRB, self._directions[self.BANKB])

        device = Mcp23017InGameDevice(name, self, pin, bank, **kwargs)
        self._indevices[bank].append(device)
        self._devices.append(device)
        return device

    def sync(self):
        # Set ouptut devices bank A
        if self._dirty[self.BANKA]:
            self._dirty[self.BANKA] = False
            self.bus.write_byte_data(
                self._address, self.OLATA, self._state[self.BANKA])

        # Set ouptut devices bank B
        if self._dirty[self.BANKB]:
            self._dirty[self.BANKB] = False
            self.bus.write_byte_data(
                self._address, self.OLATB, self._state[self.BANKB])

        # Load input devices bank A
        if self._indevices[self.BANKA]:
            state = self.bus.read_byte_data(self._address, self.GPIOA)
            self._parseIn(self._indevices[self.BANKA], state)

        # Load input devices bank B
        if self._indevices[self.BANKB]:
            state = self.bus.read_byte_data(self._address, self.GPIOB)
            self._parseIn(self._indevices[self.BANKB], state)

    def activate(self, device):
        self._state[device.bank] |= device.pin
        self._dirty[device.bank] = True

    def deactivate(self, device):
        self._state[device.bank] &= (~device.pin)
        self._dirty[device.bank] = True

    def _parseIn(self, devices, state):
        for device in devices:
            devstate = state & device.pin
            if device.oldstate != devstate:
                device.oldstate = devstate
                device.inform(devstate)


class Mcp23017OutGameDevice(OutGameDevice):

    def __init__(self, name, hwdevice, pin, bank):
        OutGameDevice.__init__(self, name, hwdevice)
        self.pin = (1 << pin)
        self.bank = bank


class Mcp23017InGameDevice(InGameDevice):

    def __init__(self, name, hwdevice, pin, bank, **kwargs):
        InGameDevice.__init__(self, name, hwdevice, **kwargs)
        self.pin = (1 << pin)
        self.bank = bank   # pin on Bank A or Bank B
        self.oldstate = 0  # Known state, variable controlled by Mcp23017
