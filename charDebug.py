# this will be used to build graphics easier
# all digit places correspond to the following, from left to right:
# 0: raw data character
# 1: ASCII character (if available)
# 2: blank space
# 3-4: Hex value
# 5-7: Decimal value
# Dots: MSB Binary value
import digitalio
import board
import time
import core
import bcdraw
import busio
# set up a 3x4 keypad
pad = core.numpad([board.GP0, board.GP1, board.GP4, board.GP5],[board.GP7, board.GP27, board.GP26])
mosi = board.GP3
clk = board.GP2
cs = digitalio.DigitalInOut(board.GP6)
spi = busio.SPI(clk, MOSI=mosi)
screen = bcdraw.BCDRaw(spi, cs, 8)
def render(n): # converts number into led format and shows it
    screen.clear()
    screen.set_num(n, pos=7)
    screen.set_num(n, base=16, pos=4)
    screen.set_string(chr(n), pos=1)
    screen.set_dig(n, 0)
    for i in range(8):
        if n & (1 << 7-i):
            screen.buffer[i] |= 0x80
    screen.show()
def toint(s): # converts keypad sequence into integer
    st = 0 # subtotal
    for n in s:
        if n == 10 or n == 12:
            return st, True # sequence has concluded
        st *= 10
        st += n if n < 10 else 0      
    return min(st,255), len(s)==3 # sequence has not concluded, unless it has 3 digits
confirmed = 0 # number we are displaying, if confirmed
while True:
    s = pad.checksequence()
    if s:
        if s != [10] and s != [12]:
            a,b = toint(s)
            render(a)
            if b:
                confirmed = a
                pad.clearsequence()
        elif s == [10]:
            confirmed -= 1
            confirmed %= 256
            render(confirmed)
            pad.clearsequence()
        else:
            confirmed += 1
            confirmed %= 256
            render(confirmed)
            pad.clearsequence()