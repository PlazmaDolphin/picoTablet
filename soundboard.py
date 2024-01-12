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

# The listed mp3files will be played in order
mp3files = ["/sd/bone.mp3", "/sd/boom.mp3", "/sd/awp.mp3"]

# You have to specify some mp3 file when creating the decoder
mp3 = open(mp3files[0], "rb")
decoder = MP3Decoder(mp3)
audio = AudioOut(board.GP28)

while True:
    for filename in mp3files:
        # Updating the .file property of the existing decoder
        # helps avoid running out of memory (MemoryError exception)
        decoder.file = open(filename, "rb")
        audio.play(decoder)
        print("playing", filename)

        # This allows you to do other things while the audio plays!
        while audio.playing:
            pass