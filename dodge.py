import math
import random
#individual segment aliases
DOT = 0b10000000
TOP = 0b01000000
MID = 0b00000001
BOT = 0b00001000
H = [0, BOT, MID, TOP]
#game dataclass
class dodge:
    def __init__(self, lives, speed=1):
        self.safe = random.randint(1, 5)
        self.lives = lives
        self.score = 0
        self.scalespeed = speed
        self.speed = 1
        self.height = 0
        self.pos = 0
        self.slamcharge = 0.0
    def objspawn(self): #somewhere that isn't where it already is
        self.safe += random.randint(1, 5)
        self.safe %= 6
    def collision(self): #collision detection
        if self.safe == self.pos:
            self.score += 1
            self.speed += 1
            return False
        self.lives -= 1
        self.speed /= 2
        return True
    def moveobj(self):
        self.height -= 1
        self.height %= 4
        if not self.height:
            self.collision()
            self.objspawn()
    def reset(self, lives, speed=1):
        self.__init__(lives, speed)#reset game
    def move(self, direction): #direction: False = left, True = right
        if direction:
            self.pos += 1
        else:
            self.pos -= 1
        self.pos %= 6
    def getspeed(self):
        spd = math.sqrt(self.speed)*self.scalespeed
        return 1 / spd
    def slam(self, subtime):
        if not self.collision():
            self.slamcharge += subtime+self.height
            if self.slamcharge >= 5:
                self.slamcharge -= 5
                self.score += 1
        self.height = 0
        self.objspawn()
    def dump(self): #take a dump :p
        return {'lives': self.lives, 'score': self.score, 'speed': self.speed, 'height': self.height, 'pos': self.pos, 'safe': self.safe}