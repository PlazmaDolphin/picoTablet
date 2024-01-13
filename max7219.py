import digitalio
from adafruit_bus_device import spi_device
from micropython import const

try:
    import typing  # pylint: disable=unused-import
    import busio
except ImportError:
    pass

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MAX7219.git"

# register definitions
_DIGIT0 = const(1)
_INTENSITY = const(10)

class MAX7219:
    """
    MAX2719 - driver for displays based on max719 chip_select

    :param int width: the number of pixels wide
    :param int height: the number of pixels high
    :param ~busio.SPI spi: an spi busio or spi bitbangio object
    :param ~digitalio.DigitalInOut chip_select: digital in/out to use as chip select signal
    :param int baudrate: for SPIDevice baudrate (default 8000000)
    :param int polarity: for SPIDevice polarity (default 0)
    :param int phase: for SPIDevice phase (default 0)
    """

    def __init__(
        self,
        spi: busio.SPI,
        cs: digitalio.DigitalInOut,
        *,
        width: int = 8,
        height: int = 8,
        baudrate: int = 8000000,
        polarity: int = 0,
        phase: int = 0
    ):

        self._chip_select = cs
        self._chip_select.direction = digitalio.Direction.OUTPUT

        self._spi_device = spi_device.SPIDevice(
            spi, cs, baudrate=baudrate, polarity=polarity, phase=phase
        )

        self.buffer = bytearray((height // 8) * width)

        self.width = width
        self.height = height

        self.init_display()

    def init_display(self) -> None:
        """Must be implemented by derived class (``matrices``, ``bcddigits``)"""

    def clear(self) -> None:
        """
        Clears the display.
        """
        self.buffer = bytearray((self.height // 8) * self.width)
        self.show()

    def brightness(self, value: int) -> None:
        """
        Controls the brightness of the display.

        :param int value: 0->15 dimmest to brightest
        """
        if not 0 <= value <= 15:
            raise ValueError("Brightness out of range")
        self.write_cmd(_INTENSITY, value)

    def roll_right(self) -> None:
        """
        Rolls the display to the right until the rightmost digit is not blank.
        """
        while self.buffer[-1] == 0:
            self.buffer = self.buffer[1:] + self.buffer[:1]

    def show(self) -> None:
        """
        Updates the display.
        """
        for ypos in range(8):
            self.write_cmd(_DIGIT0 + ypos, self.buffer[7-ypos])

    def set_dig(self, b, p): #byte, position
        self.buffer[p] = b

    def write_cmd(self, cmd: int, data: int) -> None:
        """
        Writes a command to spi device.

        :param int cmd: register address to write data to
        :param int data: data to be written to commanded register
        """
        #print('cmd {} data {}'.format(cmd,data))
        self._chip_select.value = False
        with self._spi_device as my_spi_device:
            my_spi_device.write(bytearray([cmd, data]))
    def set_dot(self, dig, state):
        if state:
            self.buffer[dig] |= 0x80
        else:
            self.buffer[dig] &= 0x7F