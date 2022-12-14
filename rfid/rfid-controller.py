import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import spidev
from time import sleep
import requests as req


class NFC():
    def __init__(self, bus=0, device=0, spd=1000000):
        self.reader = SimpleMFRC522()
        self.close()
        self.boards = {}

        self.bus = bus
        self.device = device
        self.spd = spd

    def reinit(self):
        self.reader.READER.spi = spidev.SpiDev()
        self.reader.READER.spi.open(self.bus, self.device)
        self.reader.READER.spi.max_speed_hz = self.spd
        self.reader.READER.MFRC522_Init()

    def close(self):
        self.reader.READER.spi.close()

    def addBoard(self, rid, pin):
        self.boards[rid] = pin

    def selectBoard(self, rid):
        if not rid in self.boards:
            print("readerid " + rid + " not found")
            return False

        for loop_id in self.boards:
            GPIO.setup(self.boards[loop_id], GPIO.OUT, initial=GPIO.LOW)

            if loop_id == rid:
                GPIO.output(self.boards[loop_id], GPIO.HIGH)

        sleep(0.1)
        return True

    def read(self, rid):
        if not self.selectBoard(rid):
            return None

        self.reinit()
        cid, val = self.reader.read_no_block()
        self.close()

        return cid, val

    def write(self, rid, value):
        if not self.selectBoard(rid):
            return False

        self.reinit()
        self.reader.write_no_block(value)
        self.close()
        return True

def getTagID(rid):
    sleep(0.3)
    id, text = nfc.read(rid)
    return id

def nameTagID(id):   #Here we are going to name IDs.
 # A-APPLE
    if id == 584183260835 or id == 584186013337:
        return "A"
 # B-SWEETS
    if id == 584187520736 or id == 584187782631 or id == 584198137414:
        return "B"
 # C-BREAD
    if id == 584187717092 or id == 584187586273:
        return "C"
 # D-TEA
    if id == 584195450473 or id == 584198071873:
        return "D"
 # E-CHILI
    if id == 584190994133 or id == 584190600915:
        return "E"
 # F-EGG
    if id == 584193549836 or id == 584189159368:
        return "F"
 # DEV - tag to show the dev menu
    if id == 972025895400:
        return "DEV"
 # BACK - tag "back" in the history of pages
    if id == 313744567244:
        return "BACK"
 # RESTART:
    if id == 584190535378 or id == 584193615373:
        return "RESTART"
    else:
     #undefined ID or none
        return "x"

def compareTagID(oldTag,newTag):
    if oldTag!=newTag:
        return True
    else:
        return False

#adding global ID variables to store previous IDs.
oldID1=0
oldID2=0
oldID3=0

if __name__ == "__main__":
    nfc = NFC()
    GPIO.setwarnings(False)
    nfc.addBoard("reader1",29)
    nfc.addBoard("reader2",31)
    nfc.addBoard("reader3",33)

    while True:
        try:
            newID1=getTagID("reader1")
            newID2=getTagID("reader2")
            newID3=getTagID("reader3")

            ID1=nameTagID(newID1)
            ID2=nameTagID(newID2)
            ID3=nameTagID(newID3)

            if (compareTagID(oldID1,newID1) == True or compareTagID(oldID2,newID2) == True or compareTagID(oldID3,newID3) == True):
                choice = ID1 + "-" + ID2 + "-" + ID3
                print(choice)
                req.get('http://localhost:3000/publish/choice-msg/' + choice)
            else:
                pass
            oldID1=newID1
            oldID2=newID2
            oldID3=newID3


        finally:
            GPIO.cleanup()

        if GPIO.getmode() is None:
            GPIO.setmode(10)
