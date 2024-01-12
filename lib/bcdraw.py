# SPDX-FileCopyrightText: 2017 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_max7219.bcddigits.BCDDigits`
====================================================
"""
from micropython import const
from math import floor, log
import max7219

try:
    # Used only for typing
    from typing import List
    import digitalio
    import busio
except ImportError:
    pass

_DECODEMODE = const(9)
_SCANLIMIT = const(11)
_SHUTDOWN = const(12)
_DISPLAYTEST = const(15)
_CHAR_MAP = {
    '0': 0x7e, '1': 0x30, '2': 0x6d, '3': 0x79,
    '4': 0x33, '5': 0x5b, '6': 0x5f, '7': 0x70,
    '8': 0x7f, '9': 0x7b, 'a': 0x77, 'b': 0x1f,
    'c': 0x4e, 'd': 0x3d, 'e': 0x4f, 'f': 0x47,
    'g': 0x7b, 'h': 0x17, 'i': 0x30, 'j': 0x3c,
    'k': 0x57, 'l': 0x0e, 'm': 0x54, 'n': 0x15,
    'o': 0x1d, 'p': 0x67, 'q': 0x73, 'r': 0x05,
    's': 0x5b, 't': 0x0f, 'u': 0x1c, 'v': 0x3e,
    'w': 0x2a, 'x': 0x37, 'y': 0x3b, 'z': 0x6d,
    'A': 0x77, 'B': 0x1f, 'C': 0x4e, 'D': 0x3d, 
    'E': 0x4f, 'F': 0x47, 'G': 0x7b, 'H': 0x17, 
    'I': 0x44, 'J': 0x3c, 'K': 0x57, 'L': 0x0e, 
    'M': 0x54, 'N': 0x15, 'O': 0x1d, 'P': 0x67, 
    'Q': 0x73, 'R': 0x05, 'S': 0x5b, 'T': 0x0f, 
    'U': 0x1c, 'V': 0x3e, 'W': 0x2a, 'X': 0x37, 
    'Y': 0x3b, 'Z': 0x6d, ' ': 0x00, '-': 0x01, 
    '\xb0': 0x63, '.': 0x80
}
_HEX_CODES = [0x7e, 0x30, 0x6d, 0x79, 0x33, 0x5b, #use for decimal and hex
    0x5f, 0x70, 0x7f, 0x7b, 0x77, 0x1f, 0x4e, 0x3d, 0x4f, 0x47]

class BCDRaw(max7219.MAX7219):
    """
    Basic support for display on a 7-Segment BCD display controlled
    by a Max7219 chip using SPI.

    :param ~busio.SPI spi: an spi busio or spi bitbangio object
    :param ~digitalio.DigitalInOut cs: digital in/out to use as chip select signal
    :param int nDigits: number of led 7-segment digits; default 1; max 8
    """

    def __init__(self, spi: busio.SPI, cs: digitalio.DigitalInOut, nDigits: int = 8):
        self._ndigits = nDigits
        super().__init__(spi, cs, width=8, height=nDigits)

    def init_display(self) -> None:
        for cmd, data in (
            (_SHUTDOWN, 0),
            (_DISPLAYTEST, 0),
            (_SCANLIMIT, 7),
            (_DECODEMODE, 0), #no decode
            (_SHUTDOWN, 1),
        ):
            self.write_cmd(cmd, data)

        self.clear()

    def set_num(self, n, *, base=10, pos=7) -> None:
        for i in range(max(get_magnitude(n, base), 1)):
            if pos-i >= 0:
                self.set_dig(_HEX_CODES[n % base], pos-i)
            n //= base
    
    def set_float(self, f, precision=8):
        mag = get_magnitude(f)-1
        f /= 10**(mag)
        for i in range(precision):
            self.set_dig(_HEX_CODES[int(f)], i)
            if i == mag and i < precision:
                self.set_dot(i, True)
            f -= int(f)
            f *= 10

    def set_string(self, s: str, pos=0) -> None:
        """
        Display a string of characters.

        :param str s: string of characters to display
        """
        for i,c in enumerate(s):
            try:
                self.set_dig(_CHAR_MAP[c], i+pos)
            except KeyError:
                self.set_dig(0, i+pos)

    def set_raw(self, d: List[int]) -> None:
        """
        Set the raw digits.

        :param List[int] d: list of 8-bit values to set
        """
        for i in range(self._ndigits):
            self.set_dig(d[i], i)
    def get_raw(self):
        return self.buffer
            
def get_magnitude(n, base=10):
    #returns the order of magnitude of a number
    return 0 if n==0 else 1+floor(log(n, base))