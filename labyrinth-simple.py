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
        break
    time.sleep(0.01)



### Main ##################

# Puzzles
LabMain(labyrinth1)
