import digitalio
import board
import time
import core
import dodge
#pylint: disable=import-error
import bcdraw
import busio
# set up a 3x4 keypad
pad = core.numpad([board.GP0, board.GP1, board.GP4, board.GP5],[board.GP7, board.GP27, board.GP26])
CT = [[0.3, 0.5, 0.8, 1.2, 1.5, 2.0],[1, 3, 5, 8, 10, 16]] #cheat table
GAMESPEED = 1
GAMELIVES = 6
cheats = pad.checkheld()
if cheats:
    if cheats[0] <= 6:
        GAMESPEED = CT[0][cheats[0]-1]
        if len(cheats) > 1 and cheats[1] >= 7:
            GAMELIVES = CT[1][cheats[1]-7]
    else:
        GAMELIVES = CT[1][cheats[0]-7]
game = dodge.dodge(GAMELIVES, GAMESPEED)
mosi = board.GP3
clk = board.GP2
cs = digitalio.DigitalInOut(board.GP6)
spi = busio.SPI(clk, MOSI=mosi)
screen = bcdraw.BCDRaw(spi, cs, 8)
screen.brightness(3) #dim for my eyes
tick = core.countdown(game.getspeed())
def domove():
    move = pad.checkpressed()
    if move:
        if any([1 in move, 4 in move, 7 in move, 10 in move]): #left side = move left
            game.move(False)
        if any([3 in move, 6 in move, 9 in move, 12 in move]): #right side = move right
            game.move(True)
        if any([2 in move, 5 in move, 8 in move, 11 in move]): #middle = slam
            game.slam(tick.percent())
def render():
    state = game.dump()
    out = [0] * 8 #this is what i call a power move
    for i in range(6):
        if state['lives'] > i:
            out[i] |= 0x80 #dot indicates life
        if state['pos'] == i:
            out[i] |= 0x08 #bottom line indicates player position
        if state['safe'] != i: #haha, bet you've never seen |= before
            out[i] |= dodge.H[state['height']] #draws obstacles
    screen.set_raw(out)
    dots, score = divmod(state['score'], 100)
    screen.set_num(score, pos=7)
    screen.set_dot(6, (dots>>1)%2==1)
    screen.set_dot(7, dots%2==1)
    screen.show()
def endanim(score):
    screen.clear()
    screen.set_num(score, pos=7)
    screen.show()
    time.sleep(2)
    for pos in range(7,-2,-1):
        screen.clear()
        screen.set_num(score, pos=pos)
        screen.show()
        time.sleep(0.2)
    time.sleep(1)
    screen.set_string('THX4PLAY')
    screen.show()
    time.sleep(4)
    screen.clear()
    time.sleep(1)
def checkquit():
    while True:
        seq = pad.checksequence()
        if seq:
            if seq[0] == 12:
                screen.set_string("  QUIT? ")
                screen.show()
                if len(seq) > 1:
                    if seq[1] ==12:
                        #quit!
                        screen.clear()
                        screen.show()
                        pad.kill()
                        spi.deinit()
                        cs.deinit()
                        raise SystemExit
                    else:
                        pad.clearsequence()
                        screen.set_string('  START ', pos=0)
                        screen.show()
            else:
                break #resume game
    pad.clearsequence()
def main():
    screen.set_string(' START')
    screen.show()
    checkquit()
    while True:
        domove()
        if tick.expirechk():
            game.moveobj()
            tick.reset(game.getspeed())
        render()
        if game.lives == 0:
            break
    endanim(game.dump()['score'])
    game.reset(GAMELIVES, GAMESPEED)
if __name__ == '__main__':
    while True:
        main()