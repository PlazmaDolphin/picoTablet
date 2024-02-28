#Attempt a main menu; Need Keypad and MAX7219
import core
import board
import digitalio
import busio
import bcdraw
import sys

actions = [" DODGE  ", " SOUND  ", "CHARTEST", " QUIT?  "]

pad = core.numpad([board.GP0, board.GP1, board.GP4, board.GP5],[board.GP7, board.GP27, board.GP26])
mosi = board.GP3
clk = board.GP2
cs = digitalio.DigitalInOut(board.GP6)
spi = busio.SPI(clk, MOSI=mosi)
screen = bcdraw.BCDRaw(spi, cs, 8)

screen.set_string(" SELECT ", pos=0)
screen.show()

def execute(action):
    # free hardware for new program
    #pylint: disable=global-statement
    global pad, spi, cs
    pad.kill()
    screen.clear()
    screen.show()
    spi.deinit()
    cs.deinit()
    try:
        if action == 1:
            #pylint: disable=exec-used
            exec(open("dodgeMain.py", "r", encoding="utf-8").read())
        elif action == 2:
            #pylint: disable=exec-used
            exec(open("soundboard.py", "r", encoding="utf-8").read())
        elif action == 3:
            #pylint: disable=exec-used
            exec(open("charDebug.py", "r", encoding="utf-8").read())
    except SystemExit:
        #control given back, reinitialize hardware
        pad = core.numpad([board.GP0, board.GP1, board.GP4, board.GP5],[board.GP7, board.GP27, board.GP26])
        spi = busio.SPI(clk, MOSI=mosi)
        cs = digitalio.DigitalInOut(board.GP6)
        screen.__init__(spi, cs, 8)
        screen.set_string(" SELECT ", pos=0)
        screen.show()
    if action == 4:
        #shut down
        sys.exit()

while True:
    seq = pad.checksequence()
    if seq:
        if seq[0] < 5:
            screen.set_string(actions[seq[0]-1], pos=0)
            screen.show()
            if len(seq) > 1:
                if seq[1] ==12:
                    execute(seq[0])
                else:
                    pad.clearsequence()
                    screen.set_string(" SELECT ", pos=0)
                    screen.show()
        else:
            pad.clearsequence()