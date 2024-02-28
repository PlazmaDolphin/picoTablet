import board
from audiomp3 import MP3Decoder
from audiopwmio import PWMAudioOut as AudioOut
import busio
import sdcardio
import storage
import digitalio
import bcdraw
import core

mosi = board.GP3
clk = board.GP2
cs2 = digitalio.DigitalInOut(board.GP6)
spi2 = busio.SPI(clk, MOSI=mosi)
screen = bcdraw.BCDRaw(spi2, cs2, 8)
spi = busio.SPI(board.GP10, board.GP11, board.GP8)
cs = board.GP9
sd = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sd)
storage.mount(vfs, '/sd')
screen.brightness(3)
screen.clear()
screen.set_string("   SOUND", pos=0)
screen.show()

pad = core.numpad([board.GP0, board.GP1, board.GP4, board.GP5],[board.GP7, board.GP27, board.GP26])

mp3files = ["/sd/bone.mp3", "/sd/boom.mp3", "/sd/awp.mp3"]

# You have to specify some mp3 file when creating the decoder
mp3 = open(mp3files[0], "rb")
#pylint: disable=no-value-for-parameter
decoder = MP3Decoder(mp3)
audio = AudioOut(board.GP28)
play = False
quitscreen = False
while True:
    if not audio.playing and play: #sfx just ended
        audio.stop()
        print("stopped")
        screen.clear()
        screen.set_string("   SOUND", pos=0)
        screen.show()
        play=False
    key = pad.checkpressed()
    if len(key) > 0:
        key = key[0]
    else:
        continue
    if key == 12: #quit
        if quitscreen:
            sd.deinit()
            audio.stop()
            audio.deinit()
            decoder.file.close()
            pad.kill()
            spi.deinit()
            storage.umount('/sd')
            cs2.deinit()
            spi2.deinit()
            raise SystemExit
        quitscreen = True
        screen.clear()
        screen.set_string("  QUIT? ", pos=0)
        screen.show()
    else:
        quitscreen = False
    if key <= 3:
        try:
            decoder.file.close()
            audio.stop()
            decoder.file = open(mp3files[key-1], "rb")
            audio.play(decoder)
            print("playing", mp3files[key-1])
            screen.clear()
            screen.set_string(mp3files[key-1].split("/")[-1].split(".")[0], pos=0)
            screen.show()
            play = True
        except OSError:
            print("Slow down idiot")
            decoder.file.close()
            audio.stop()
    if key == 4: #pause/resume
        if play:
            audio.pause()
            print("paused")
            screen.clear()
            screen.set_string("-PAUSED-", pos=0)
            screen.show()
            play=False
        else:
            audio.resume()
            print("resumed")
            screen.clear()
            screen.set_string("-RESUME-", pos=0)
            screen.show()
            play=True
    if key == 5: #stop
        audio.stop()
        print("stopped")
        screen.clear()
        screen.set_string("= STOP =", pos=0)
        screen.show()
        play=False