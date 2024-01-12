import board
from audiomp3 import MP3Decoder
from audiopwmio import PWMAudioOut as AudioOut
import core
import busio
import sdcardio
import storage

spi = busio.SPI(board.GP10, board.GP11, board.GP8)
sd = sdcardio.SDCard(spi, board.GP9)
vfs = storage.VfsFat(sd)
storage.mount(vfs, '/sd')

pad = core.numpad([board.GP0, board.GP1, board.GP4, board.GP5],[board.GP7, board.GP27, board.GP26])

mp3files = ["/sd/bone.mp3", "/sd/boom.mp3", "/sd/awp.mp3"]

# You have to specify some mp3 file when creating the decoder
mp3 = open(mp3files[0], "rb")
decoder = MP3Decoder(mp3)
audio = AudioOut(board.GP28)
play = False
while True:
    if not audio.playing and play: #sfx just ended
        audio.stop()
        print("stopped")
        play=False
    key = pad.checkpressed()
    if len(key) > 0:
        key = key[0]
    else:
        continue
    if key <= 3:
        try:
            decoder.file.close()
            audio.stop()
            decoder.file = open(mp3files[key-1], "rb")
            audio.play(decoder)
            print("playing", mp3files[key-1])
            play = True
        except OSError:
            print("Slow down idiot")
            decoder.file.close()
            audio.stop()
    if key == 4: #pause/resume
        if play:
            audio.pause()
            print("paused")
            play=False
        else:
            audio.resume()
            print("resumed")
            play=True
    if key == 5: #stop
        audio.stop()
        print("stopped")
        play=False