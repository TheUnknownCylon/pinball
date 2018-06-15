from pinball.gamedevices.gamedevice import GameDevice


class Led(GameDevice):
    """
    Represents a single color LED device.
    The LED can be turned on or off.
    """

    def __init__(self, led):
        GameDevice.__init__(self)
        self._led = led

    def on(self):
        self._led.activate()

    def off(self):
        self._led.deactivate()


class PwmLed(Led):
    """
    Represents a single color LED device, of which the brightnes
    can be controlled.
    """

    def __init__(self, pwmOutDevice, value=0xFF):
        Led.__init__(self, pwmOutDevice)
        self._pwmOutDevice = pwmOutDevice
        self._ratio = self._pwmOutDevice.maxIntensity() / 0xFF

    def set(self, value):
        """
        Set the brightness, using a 2 byte value.

        @param value Led brightness, between 0x00 and 0xFF
        """
        # TODO, is this faster?: lambda x: ((x+1)<<(pwm_bits - 8)) - 1
        intensity = round(self._ratio * value)
        self._pwmOutDevice.setIntensity(intensity)

    def setRawValue(self, value):
        self._pwmOutDevice.setIntensity(value)


class RGBLed(GameDevice):
    """
    Device that combines three PwmLeds as an RGB led.
    """

    def __init__(self, pwmled_red, pwmled_green, pwmled_blue):
        self._r = pwmled_red
        self._g = pwmled_green
        self._b = pwmled_blue

    def on(self):
        self._r.on()
        self._g.on()
        self._b.on()

    def off(self):
        self._r.off()
        self._g.off()
        self._b.off()

    def set(self, rgbvalue):
        """
        Sets the color of the RGB led, using a 2 bytes/color hex-based RGB value,
        e.g. 0xFFFFFF for white, 0x000000 for black (off).

        @param value The led color to set, hex rgb value
        """
        self._r.set(rgbvalue >> 16)
        self._g.set(0xFF & (rgbvalue >> 8))
        self._b.set(0xFF & rgbvalue)
