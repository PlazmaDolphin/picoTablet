import digitalio
import pwmio
import board
import time
notes = {'C': 262, 'C#': 277, 'D': 294, 'D#': 311,
    'E': 330, 'F': 349, 'F#': 370, 'G': 392,
    'G#': 415, 'A': 440, 'A#': 466, 'B': 494
}
numnotes = [262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494]
fontA = { #letters
     ' ': 0b00000000, 'A': 0b01110111, 'B': 0b01111100,
     'C': 0b00111001, 'c': 0b01011000, 'D': 0b01011110,
     'E': 0b01111001, 'F': 0b01110001, 'G': 0b01111101,
     'g': 0b01101111, 'H': 0b01110110, 'h': 0b01110100,
     'I': 0b00010001, 'J': 0b00011111, 'j': 0b00001110,
     'K': 0b01110110, 'L': 0b00111000, 'l': 0b00000110,
     'l2':0b00110000, 'M': 0b00010101, 'N': 0b00110111,
     'n': 0b01010100, 'n2':0b00100011, 'O': 0b00111111,
     'o': 0b01011100, 'o2':0b01100011, 'P': 0b01110011,
     'Q': 0b01100111, 'R': 0b01010000, 'S': 0b01101101,
     'T': 0b01111000, 'U': 0b00111110, 'u': 0b00011100,
     'u2':0b01100010, 'V': 0b01110010, 'W': 0b00101010,
     'X': 0b01110110, 'Y': 0b01101110, 'Z': 0b01011011,
     #numbers
     '1': 0b00000110, '2': 0b01011011, '3': 0b01001111,
     '4': 0b01100110, '5': 0b01101101, '6': 0b01111101,
     '7': 0b00000111, '8': 0b01111111, '9': 0b01101111,
     '0': 0b00111111,
     #symbols
     '-': 0b01000000, '_': 0b00001000, '=': 0b01001000,
     ',': 0b00000100, "'": 0b00000010, '?': 0b11010011,
     '"': 0b00100010
     }
numfont = [0b00111111, 0b00000110, 0b01011011, 0b01001111, 0b01100110,
           0b01101101, 0b01111101, 0b00000111, 0b01111111, 0b01101111,
           0b01110111, 0b01111100, 0b00111001, 0b01011110, 0b01111001, 0b01110001] #hex A-F
padnums = [['1', '2', '3'],['4', '5', '6'],['7', '8', '9'],['*','0','#']]
def toseg(string): #converts string to binary 7seg array
    letters = []
    for i in string:
        letters.append(fontA[i])
    return letters

class countdown:
    def __init__(self, t):
        self.start = time.monotonic_ns()
        self.finish = self.start + t * 1000000000
    def display(self):
        times = (self.finish - time.monotonic_ns())//10000000
        ms = times%100 #actually centiseconds but who cares
        times = int(times/100)
        secs = times % 60
        mins = int(times / 60)
        tint = 0
        if mins:
            tint += mins*100
            tint += secs
        else:
            tint += secs*100
            tint += ms
        return tint
    def buzzbend(self, SN, EN):
        ET = self.finish - self.start
        NT = time.time() - self.start
        X = ET / NT
        D = EN / SN
        C = D / X
        return SN + C
    def expirechk(self):
        return time.monotonic_ns() > self.finish

class buzzer:
    def __init__(self, pin):
        self.buzz = pwmio.PWMOut(pin, duty_cycle=0, frequency=440, variable_frequency=True)
        self.BN1 = 0
        self.BN2 = 0
        self.bend = None
    def playnote(self, note, octave):
        octave -= 4
        self.playfreq(notes[note]*(2 ** octave))#not sure if powers work with negatives
    def playnum(self, num, octave):
        octave -= 4
        self.playfreq(numnotes[num]*(2 ** octave))
    def playfreq(self, freq):
        self.buzz.duty_cycle = 2**15
        self.buzz.frequency = int(freq)
    def rest(self):
        self.buzz.duty_cycle = 0
    def setbend(self, N, btime):
        self.BN1 = self.buzz.frequency
        self.bend = countdown(btime)
        self.BN2 = N
    def bendn(self):
        if self.bend != None:
            self.buzz.frequency = self.bend.buzzbend(self.BN1, self.BN2)
            if self.bend.expirechk():
                self.bend = None

class numpad:
    def __init__(self, rpins, cpins): #rows are input, collumns are output
        self.rows = []
        self.cols = []
        for p in rpins:
            a = digitalio.DigitalInOut(p)
            a.direction = digitalio.Direction.OUTPUT
            self.rows.append(a)
        for p in cpins:
            a = digitalio.DigitalInOut(p)
            a.direction = digitalio.Direction.INPUT
            a.pull = digitalio.Pull.DOWN
            self.cols.append(a)
    def check(self):
        out = []
        for r in self.rows:
            r.value = True
            rval = []
            for c in self.cols:
                rval.append(c.value)
            r.value = False
            out.append(rval)
        return out
    def checklet(self):
        out = ''
        for ir in range(len(self.rows)):
            self.rows[ir].value = True
            for ic in range(len(self.cols)):
                if self.cols[ic].value:
                    out += padnums[ir][ic]
            self.rows[ir].value = False
        return out

class button:
    def __init__(self, pin):
        btn = digitalio.DigitalInOut(pin)
        btn.direction = digitalio.Direction.INPUT
        btn.pull = digitalio.Pull.DOWN
        self.btn = btn
        self.last = False
    def get(self):
        #0-Off 1-Pressed 2-Released 3-Held
        status = 0
        if self.last:
            status += 2
        if self.btn.value:
            status += 1
        self.last = self.btn.value
        return status