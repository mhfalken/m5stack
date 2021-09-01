# Michael Hansen 2021, Coding Pirates Furesø, Denmark, www.rclab.dk
# M5Stack Core 2, Color and Light sensor, lock with code 385
# All files in sd/ should be put in the root of an SD card 
from m5stack import *
from m5stack_ui import *
from uiflow import *
from m5stack import touch
import time
import uos
import unit

### Image Library ##################

def ImagesCopy(filenamesIn):
  """ Copy image(s) from SD card to flash"""
  if type(filenamesIn) == type([]):
    filenames = filenamesIn
  else:
    filenames = [filenamesIn]
  for fn in filenames:
    fr = open('/sd/%s' %fn, "rb")
    fw = open('/flash/img/%s' %fn, "wb")
    fw.write(fr.read())
    fr.close()
    fw.close()

def ImagesCleanup(filenamesIn):
  """ Delete files from flash"""
  if type(filenamesIn) == type([]):
    filenames = filenamesIn
  else:
    filenames = [filenamesIn]
  for fn in filenames:
    uos.remove('/flash/img/%s' %fn)

def ImagesShow(filenamesIn, posx, posy, count=1, delayMs=1):
  """ Show a list of images in a round robin (animating effect) """
  if type(filenamesIn) == type([]):
    filenames = filenamesIn
  else:
    filenames = [filenamesIn]
  for i in range(count):
    for fn in filenames:
      lcd.image(posx, posy, "/flash/img/%s" %fn)
      if delayMs > 0:
        time.sleep(delayMs/1000)

def ImageMove(filename, posx, posy, stepx, stepy, count=10, delayMs=1):
  """ Move an image """
  for i in range(count):
    lcd.image(posx+i*stepx, posy+i*stepy, "/flash/img/%s" %filename)
    if delayMs > 0:
      time.sleep(delayMs/1000)


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
  #lcd.print("%f" %v, 200, 1, 0xff0000)
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
  lcd.print("Escape Room", 20, 0, 0x80ff80)
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

### 9 Puzzle ##################

btnSize = 65
btnXList = [60, 130, 199]
btnYList = [20, 90, 159]

def BtnPressed():
  while True:
    if touch.status():
      (tx, ty) = touch.read()
      #lcd.print("%i %i" %(tx, ty), 0, 100, 0xffffff)
      btn = 1
      for y in btnYList:
        for x in btnXList:
          if tx > x and tx < (x+btnSize) and ty > y and ty < (y+btnSize):
            #lcd.print("%i" %btn, 0, 0, 0xffffff)
            speaker.playWAV('/sd/pop.wav', 44100, speaker.F16B)
            return btn
          btn += 1
    StatusLine()

def Img9Print(fnameList, imgNoList, btnNo):
  imgNo = 0
  for y in btnYList:
    for x in btnXList:
      if imgNo == btnNo-1:
        ImagesShow(fnameList[imgNoList[imgNo]-1], x, y)
      imgNo += 1

def Puzzle9():
  """9 Puzzle game. Swap by touching 2 different image tiles """
  img9List = ["er9p_1.jpg", "er9p_2.jpg", "er9p_3.jpg", "er9p_4.jpg", "er9p_5.jpg", 
             "er9p_6.jpg", "er9p_7.jpg", "er9p_8.jpg", "er9p_9.jpg"]
  lcd.clear()
  ImagesCopy(img9List)

  imgNoList = [3,5,2,9,7,4,8,6,1]
  #imgNoList = [2,1,3,4,5,6,7,8,9]  # Test
  for btnNo in range(9):
    Img9Print(img9List, imgNoList, btnNo+1)

  while True:
    btn1 = BtnPressed()
    wait_ms(200)
    btn2 = BtnPressed()
    if btn1 == btn2:
      continue
    no1 = imgNoList[btn1-1]
    no2 = imgNoList[btn2-1]
    imgNoList.remove(no1)
    imgNoList.remove(no2)
    if btn1 < btn2:
      imgNoList.insert(btn1-1, no2)
      imgNoList.insert(btn2-1, no1)
    else:
      imgNoList.insert(btn2-1, no1)
      imgNoList.insert(btn1-1, no2)
    speaker.playWAV('/sd/click.wav', 44100, speaker.F16B)
    Img9Print(img9List, imgNoList, btn1)
    Img9Print(img9List, imgNoList, btn2)

    for i in range(9):
      if imgNoList[i] != i+1:
        break
      if i == 8:
        # Puzzle finish
        fn = "done.jpg"
        ImagesCopy(fn)
        ImagesShow(fn, 115, 60)
        ImagesCleanup(fn)
        speaker.playWAV('/sd/tadar.wav', 44100, speaker.F16B)
        ImagesCleanup(img9List)
        time.sleep(3)
        return

### RGB Sensor ##################

def ColorCmp(color1, color2):
  for i in range(3):
    c1 = color1 & 0xff
    c2 = color2 & 0xff
    if abs(c1-c2) > 0x50:
      return False
    color1 >>= 8
    color2 >>= 8
  return True

def PuzzleColor_():
  colorList = [0x1010f0, 0xff0000, 0x00c000, 0xffff00]
  #colorList = [0x0000ff] # Test
  lcd.clear()
  StatusLine(True)
  # Display image with code to unlock
  fn = "er385.jpg"
  ImagesCopy(fn)
  ImageMove(fn, 1, 90, 4, 0, 28)
  ImagesCleanup(fn)
  # Display RGB hint
  lcd.circle(10, 200, 5, 0xff0000, 0xff0000)
  lcd.circle(10, 210, 5, 0x00ff00, 0x00ff00)
  lcd.circle(10, 220, 5, 0x0000ff, 0x0000ff)

  # Wait for RGB module
  lcd.font(lcd.FONT_DejaVu24)
  while True:
    StatusLine()
    try:
      colorMod = unit.get(unit.COLOR, (32,33))
      break
    except:
      wait_ms(100)
      continue

  lcd.clear()
  StatusLine(True)
  # Display challange
  x = 85
  for c in colorList:
    lcd.rect(x, 100, 30, 50, c, c)
    x += 40

  colorNo = 0
  while True:
    r = colorMod.red
    g = colorMod.green
    b = colorMod.blue
    color = r<<16 | g<<8 | b
    # Display current RGB module color
    lcd.circle(160, 50, 20, color, color)
    res = ColorCmp(color, colorList[colorNo])
    if res == 1:
      speaker.playWAV('/sd/bell.wav', 44100, speaker.F16B)
      lcd.rect(85+40*colorNo, 100, 30, 50, 0xffffff, colorList[colorNo])
      colorNo += 1
      if colorNo == len(colorList):
        # Puzzle finish
        fn = "done.jpg"
        ImagesCopy(fn)
        ImagesShow(fn, 115, 60)
        ImagesCleanup(fn)
        speaker.playWAV('/sd/tadar.wav', 44100, speaker.F16B)
        time.sleep(3)
        return

        break
    #lcd.rect(0, 220, 310, 20, 0x0, 0x0)
    #lcd.print("%2x, %2x, %2x" %(r, g, b), 50, 220, 0xffffff)
    
    StatusLine()
    wait_ms(300)

def PuzzleColor():
  """ Attach Color module and select the correct color sequence """
  while True:
    try:
      PuzzleColor_()
      break
    except:
      pass

def PuzzleLight():
  lightGates = [(20, 20), (70, 18), (40, 15), (100, 9), (10, 7)]
  adc0 = machine.ADC(33)
  adc0.atten(machine.ADC.ATTN_11DB)
  adc0.width(machine.ADC.WIDTH_10BIT)
  lcd.clear()
  StatusLine(True)
  lcd.font(lcd.FONT_DejaVu24)

  # Display light hint
  lcd.circle(11, 200, 7, 0xffffff, 0xffffff)
  lcd.line(4, 191, 18, 208, 0xffffff)
  lcd.line(4, 208, 18, 191, 0xffffff)
  lcd.line(1, 200, 22, 200, 0xffffff)
  lcd.line(11, 189, 11, 210, 0xffffff)

  #light = unit.get(unit.LIGHT, (32,33))
  # Can't use this function as it can't handle the unit change on the fly!!!

  # Display challange
  gateX = 85
  gateY = 70
  gateDx = 30
  gateDy = 128
  lcd.rect(gateX-gateDx, gateY, gateDx*(len(lightGates)+1), gateDy, 0xffffff, 0x0)
  x = gateX
  for gate in lightGates:
    lcd.rect(x, gateY, 10, gate[0], 0xffffff, 0xffffff)
    lcd.rect(x, gateY + gate[0]+gate[1], 10, gateDy-(gate[0]+gate[1]), 0xffffff, 0xffffff)
    x += gateDx

  while True:
    StatusLine()
    light = 1024-adc0.read()
    if light > 1 and light < 1000:
      break

  # Light sensor found
  lastX = gateX-10
  lastY = 120
  gateNo = 0
  hit = 0
  dia = 11
  while True:
    StatusLine()
    light = 1024-adc0.read()
    gray = int(light) >> 2
    color = gray << 16 | gray << 8 | gray
    lcd.circle(150, 30, 15, 0xffffff, color)
    
    posY = gray >> 1
    if posY < 8:
      posY = 8
    if posY > 120:
      posY = 120
    y = gateY+gateDy-posY
    lcd.circle(lastX, lastY, int(dia/2), 0x0, 0x0)
    gate = lightGates[gateNo]
    val = 128-posY
    if val > gate[0] and val < gate[0] + gate[1]:
      hit += 1
    else:
      hit = 0
    if hit > gateNo+1:
      lastX += gateDx
      gateNo += 1
      dia -= 1
      if gateNo == len(lightGates):
        # Done
        fn = "done.jpg"
        ImagesCopy(fn) 
        ImagesShow(fn, 115, 60)
        ImagesCleanup(fn)
        speaker.playWAV('/sd/tadar.wav', 44100, speaker.F16B)
        time.sleep(3)
        return
    lcd.circle(lastX, y, int(dia/2), 0x00ffff, 0x00ffff)
    lastY = y

    #lcd.rect(0, 220, 310, 20, 0x0, 0x0)
    #lcd.print("%i" %(light.analogValue), 50, 220, 0xffffff)
    wait_ms(300)


### Main ##################

Splash() 
startTimeS = time.time()

# Puzzles
Puzzle9()
PuzzleColor()
PuzzleLight()

End()
