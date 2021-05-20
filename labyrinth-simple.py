# Labyrinth game
# Michael Hansen 2021, Coding Pirates Furesø, Denmark, www.rclab.dk
# M5Stack Core 2

from m5stack import *
from m5stack_ui import *
from uiflow import *
from m5stack import touch
import time
import uos
import unit
import imu

### Time/battery ##################

startTimeS = 0
lastTimeS = -1
def TimePrint():
  global lastTimeS
  global startTimeS
  nextTimeS = time.time() - startTimeS
  if nextTimeS == lastTimeS:
    return
  m = lastTimeS / 60
  s = lastTimeS % 60
  lcd.font(lcd.FONT_DejaVu18)
  lcd.print("%02i:%02i" %(m, s), 10, 1, 0x0)
  lastTimeS = nextTimeS
  m = lastTimeS / 60
  s = lastTimeS % 60
  lcd.print("%02i:%02i" %(m, s), 10, 1, 0xffff00)

battLastLines = -1
def BattPrint(force=False):
  global battLastLines
  v = power.getBatVoltage()
  lines = int((v - 3.7)*100)
  if lines < 2:
    lines = 2
  if lines == battLastLines and not force:
    return
  battLastLines = lines
  x = 250
  lcd.rect(x-1, 1, 52, 12, 0xffffff, 0x000000)
  if lines > 20:
    color = 0x00ff00
  elif lines > 10:
    color = 0xffff00
  else:
    color = 0xff0000
  lcd.rect(x, 2, lines, 10, color, color)

def StatusLine(force=False):
  TimePrint()
  BattPrint(force)

### Splash ##################

def Splash():
  lcd.clear()
  time.sleep(1)
  lcd.font(lcd.FONT_DejaVu40)
  lcd.print("Labyrint", 70, 0, 0x80ff80)
  lcd.font(lcd.FONT_DejaVu24)
  lcd.print("v. 1.02", 110, 50, 0xffffff)
  lcd.print("Michael Hansen", 60, 88, 0xffff00)
  lcd.print("www.rclab.dk", 70, 115, 0x0000ff)
  lcd.print("Coding Pirates", 68, 150, 0xff0000)
  lcd.print("Furesoe", 110, 180, 0xff0000)
  time.sleep(2)
  lcd.print("Tryk for at starte", 50, 210, 0xffffff)

  while not touch.status():
    continue

### End ##################

def End():
  lcd.clear()
  time.sleep(1)
  lcd.font(lcd.FONT_DejaVu56)
  lcd.print("Slut", 100, 30, 0x80ff80)
  lcd.font(lcd.FONT_DejaVu40)
  usedTimeS = time.time() - startTimeS
  m = usedTimeS / 60
  s = usedTimeS % 60
  lcd.print("Tid %02i:%02i" %(m, s), 55, 130, 0xffffff)
  time.sleep(5)
  while not touch.status():
    continue

### Labyrinth ##################

labyrinth1 = [
  "XXXXXXXX",
  "X      X",
  "X XXXX X",
  "X XE   X",
  "X X XX X",
  "X    X X",
  "XXXXXXXX",
  (100, 50, 0x0000ff) ]

labyrinth2 = [
  "XXXXXXXXXXXXXXXXXXXXX",
  "X     X X           X",
  "X XXXXX X XXXXXXXXX X",
  "X  X  X    X    X   X",
  "XX XX X XXXXX X X XXX",
  "X   X    XE   X X   X",
  "XX XXX XXXXXX X   X X",
  "X    X  X   X X XXX X",
  "XXX XX  X X   X   X X",
  "X   X   XXXXXXXXXXX X",
  "XX    XXX X   X   X X",
  "X   X X     X   X   X",
  "XXXXXXXXXXXXXXXXXXXXX",
  (10, 30, 0xffff00) ]

labyrinth3 = [
  "XXXXXXXXXXXXXXXXXXXXX",
  "X            X      X",
  "XX XXXX XXXX   XXX XX",
  "X  X    X    X X    X",
  "X XXX XXX XX XXX XXXX",
  "X         X    X X EX",
  "X XXXXXXXXX XXXX X XX",
  "X   X     X X    X  X",
  "X X X X XXXXX XXXXX X",
  "XXX X X X         X X",
  "X X X X X XXXX XX X X",
  "X     X      X X    X",
  "XXXXXXXXXXXXXXXXXXXXX",
  (10, 30, 0x00ff00) ]



def LabCheckPosSub(labyrinth, posX, posY, width, radius, ch):
  x = int((posX-radius)/width)
  y = int((posY-radius)/width)
  if labyrinth[y][x] == ch:
    return True
  x = int((posX+radius)/width)
  y = int((posY-radius)/width)
  if labyrinth[y][x] == ch:
    return True
  x = int((posX-radius)/width)
  y = int((posY+radius)/width)
  if labyrinth[y][x] == ch:
    return True
  x = int((posX+radius)/width)
  y = int((posY+radius)/width)
  if labyrinth[y][x] == ch:
    return True
  return False

def LabCheckPos(labyrinth, posX, posY, width, radius):
  if LabCheckPosSub(labyrinth, posX, posY, width, radius, 'X'):
    return 'X'

  if LabCheckPosSub(labyrinth, posX, posY, width, 0, 'E'):
    return 'E'

  return ' '

def LabMain(labyrinth):
  global startTimeS
  bgColor = 0
  (labXOffset, labYOffset, labColor) = labyrinth[-1]
  labWidth = 14
  kugleR = 5
  kugleX = labXOffset + labWidth + kugleR
  kugleY = labYOffset + labWidth + kugleR
  kugleColor = 0xffffff

  lcd.clear()
  StatusLine(True)
  acc = imu.IMU()

  y = labYOffset
  for line in labyrinth[0:-1]:
    x = labXOffset
    for c in line:
      if c == 'X':
        lcd.rect(x, y, labWidth, labWidth, labColor, labColor)
      if c == 'E':
        lcd.circle(x+int(labWidth/2), y+int(labWidth/2), kugleR, 0x00ff00)
      x += labWidth
    y += labWidth

  while True: #not touch.status():  # Debug
    (x, y, z) = acc.acceleration
    x = kugleX + int(-5*x)
    y = kugleY + int(5*y)
    res = LabCheckPos(labyrinth, x-labXOffset, y-labYOffset, labWidth, kugleR)
    if res != 'X':
      lcd.circle(kugleX, kugleY, kugleR, bgColor, bgColor)
      kugleX = x
      kugleY = y
      lcd.circle(kugleX, kugleY, kugleR, kugleColor, kugleColor)
      if res == 'E':
        # End
        lcd.font(lcd.FONT_DejaVu40)
        lcd.print("Done", 100, 200, 0x00ffff)
        time.sleep(2)
        startTimeS += 2
        break
    StatusLine()
    time.sleep(0.01)



### Main ##################

Splash() 
startTimeS = time.time()

# Puzzles
LabMain(labyrinth1)
LabMain(labyrinth2)
LabMain(labyrinth3)

End()
