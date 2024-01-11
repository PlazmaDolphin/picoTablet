import digitalio
# pylint: disable=import-error
import board
import time

#simple blink
T = 0.20
piLed = digitalio.DigitalInOut(board.GP25)
piLed.direction = digitalio.Direction.OUTPUT
while True:
    piLed.value = True
    time.sleep(T)
    piLed.value = False
    time.sleep(T)