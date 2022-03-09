import pyautogui
from PIL import Image
import inputManager

#16 by 25
#7, 5

numPath = "C:\\Users\\patri\\OneDrive\\Documents\\solitare ai\\numbers\\{}.png"

# Stores the card's suit and value.
class Card:
    suit = 0
    value = 0

    def __init__(self, s, v):
        self.suit = s
        self.value = v
    
    def printValue(self):
        v = str(self.value)
        if self.value == 13:
            v = "K"
        elif self.value == 12:
            v = "Q"
        elif self.value == 11:
            v = "J"
        elif self.value == 10:
            v = "T"
        elif self.value == 1:
            v = "A"
        return v

    def __str__(self):
        v = self.printValue()
        
        s = ""
        if self.suit == 0:
            s = "H"
        elif self.suit == 1:
            s = "S"
        elif self.suit == 2:
            s = "D"
        elif self.suit == 3:
            s = "C"
        else:
            s = "U"
        return "Suit: {}, Value: {}".format(s, v)

#change per screen resolution
colorSpot = (16,43)
holeBlack = (20,43)
holeRed = (22,41)

# Given an image of a card's top left corner, identifies the suit.
def getSuit(img: Image.Image):
    color = img.getpixel(colorSpot)
    if(color[0] > 0):
        hole = img.getpixel(holeRed)
        return 0 if hole[0] < 255 else 2
    else:
        hole = img.getpixel(holeBlack)
        return 1 if hole[0] < 255 else 3

# Given a screenshot, identifies a card's suit and value.
# Returns a Card object representation of the card.
def identifyCard(img: Image.Image):
    suit = getSuit(img)
    number = getNumber(img)
    value = -1
    for i in range(0,14):
        comp = Image.open(numPath.format(str(i)))
        diffs = 0
        listA = list(comp.getdata())
        listB = list(number.getdata())
        for x in range(0, len(listA)):
            if listA[x] != listB[x]:
                diffs += 1
        #print("n: {} diffs: {}".format(i,diffs))
        if diffs <= 10:
            value = i
            break
    newCard = Card(suit, value)
    return newCard

# Gets card based on coordinates
# X: The column of cards to be selected
# Y: The row of cards to be selected
# Note: For y, the pixel decreases by 1 on some numbers
# Returns Card object of card
pxDecreaseAmt = 1
numDecrease = (2, 7)
def getCard(X, Y):
    location = inputManager.getLocation(X, Y)
    sizeY = inputManager.getCardSize(Y)
    screenshot = pyautogui.screenshot(region=location + sizeY)
    return identifyCard(screenshot)

# Identify top card from the stack.
# Returns a Card object that represents the card.
def getTopCard():
    screenshot = pyautogui.screenshot(region=(inputManager.topX, inputManager.topY, inputManager.sizeX, inputManager.sizeY))
    return identifyCard(screenshot)

# Identify top card in stack pile
def getTopPile():
    screenshot = pyautogui.screenshot(region=(inputManager.topX-171, inputManager.topY, inputManager.sizeX, inputManager.sizeY))
    return identifyCard(screenshot)

#Captures number and returns screenshot. Removes red channel so that red and black cards look the same.
#change per screen resolution
numCut = (8,8,25,34)
def getNumber(img: Image.Image):
    matrix = (  0, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0)
    img = img.convert("RGB", matrix)
    num = img.crop(numCut)
    return num 

#Development purposes only! Fill first column with cards, then run this to get number images.
def getNums():
    for i in range(0,13):
        location = inputManager.getLocation(0, i)
        sizeY = inputManager.getCardSize(i)
        screenshot = pyautogui.screenshot(region=location + sizeY)
        num = getNumber(screenshot)
        num.save("C:\\Users\\patri\\OneDrive\\Documents\\solitare ai\\numbers\\{}.png".format(str(13 - i)), "PNG")