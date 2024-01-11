NOTES = [131, 139, 147, 156, 165, 175, 185, 196, 208, 220, 233, 246] #C3-B3
BASEOCT = 3
def tohz(n,o): #conversion functions
    base = NOTES[n]
    return base << o-BASEOCT if o >= BASEOCT else base >> BASEOCT-o #similar to pow() but faster
def tosec(tpm):
    tpm /= 60.0
    return 1.0 / tpm
def tonote(b):
    o,n = nib(b)
    return ['C-','C#','D-','D#','E-','F-','F#','G-','G#','A-','A#','B-'][n]+str(o)
def nib(b): #returns nibbles
    return (b>>4, b%16)
def verify(b, track):
    head = (nib(b[0])+nib(b[1])) #header
    if sum(head)%16 != 0xE:
        raise RuntimeError("Checksum Failed")
    tpm = (head[1]<<8) + b[1] #ticks per minute
    tp = [0,0] #track pointers
    for (i, n) in enumerate(b[2:]): #find beginning of track
        if n == 0x0E + track*16:
            tp[0] = i+2
            break
    else:
        raise RuntimeError("No start to track %d"%track)
    for (i, n) in enumerate(b[tp[0]:]): #find end of track
        if n == 0x0F + track*16:
            tp[1] = i+tp[0]
            break
    else:
        raise RuntimeError("No end to track %d or end before beginning"%track)
    return (tpm, tp)
'''Compiled opcodes:
0: Play(Hz)
1: Hold(Time)
2: Rest()
'''
def compileepic(file, track, hz=True):
    f = open(file, 'rb') #file
    b = bytearray(f.read()) #bytes
    tpm, tp = verify(b, track)
    tick = tosec(tpm)
    musica = []
    for n in b[tp[0]:tp[1]]:
        p, c = nib(n) #parameter, code
        if c < 0xC:
            musica.append([0, tohz(c,p)] if hz else [0, n])
            musica.append([1,tick])
        elif c == 0xC:
            musica.append([1,tick*(p+1)]) #0C = Rest 1, FC = Rest 16
        elif c == 0xD:
            musica.append([2]) #first nibble ignored, always holds for 1
            musica.append([1,tick])
        else:
            continue #for xE or xF, not music commands
    return musica
def visual(file, track):
    f = open(file, 'rb') #file
    b = bytearray(f.read()) #bytes
    _, tp = verify(b, track)
    musica = ''
    for n in b[tp[0]:tp[1]]:
        p, c = nib(n) #parameter, code
        if c < 0xC:
            musica+=tonote(n)+'\n'
        elif c == 0xC:
            musica+='---\n'*(p+1) #0C = Rest 1, FC = Rest 16
        elif c == 0xD:
            musica+='===\n'
        else:
            continue #for xE or xF, not music commands
    return musica