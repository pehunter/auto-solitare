import pyautogui
import time

# Sets properties for cursor animation
ANIMATION_ENABLED = False
ANIMATION_DURATION = 0.2
ANIMATION_EFFECT = pyautogui.easeInOutSine

#change per screen resolution
incX = 171
sizeX = 30
sizeY = 48
offsetX = 1416
offsetY = 621

pxDecreaseAmt = 3
numYDecrease = (2, 7, 12)

# Gets size of card
def getCardSize(Y):
    cardSizeY = sizeY - (pxDecreaseAmt if Y in numYDecrease else 0)
    return (sizeX, cardSizeY)

# Gets the pixel location of a card, given coordinates.
def getLocation(X, Y, subXOffset=0, subYOffset=0):
    cardY = offsetY + sizeY * Y + subYOffset
    for y in numYDecrease:
        cardY -= pxDecreaseAmt if Y > y else 0
    #print(offsetY - cardY)
    #accounts for extra X pixels
    cardX = offsetX + incX * X + subXOffset
    #print(cardX)
    return (cardX, cardY)

# Move mouse to top-middle of card.
def moveToCard(X, Y):
    location = getLocation(X,Y, sizeX*2, sizeY/2)
    #print("Location: {}, {}  -->  {}, {}".format(X, Y, location[0], location[1]))
    if(ANIMATION_ENABLED):
        pyautogui.moveTo(location[0], location[1], duration = ANIMATION_DURATION, tween=ANIMATION_EFFECT)
        time.sleep(ANIMATION_DURATION)
    else:
        pyautogui.moveTo(location[0], location[1])
    #print("Mouse: {}, {}".format(str(pyautogui.position()[0]), str(pyautogui.position()[1])))

# Get location of ace pile and move mouse there.
# (Shouldn't have to identify any card here)
aceX = 2000
aceY = 484
def moveToAce(X):
    pyautogui.moveTo(aceX + incX*X, aceY)
    

# Collect current card.
def collectCard():
    pyautogui.doubleClick()

# Move current card to different spot.
# Note: Must wait because drag does not work...
# X, Y: Coordinates of new spot.
def dragTo(X, Y):
    pyautogui.mouseDown()
    moveToCard(X, Y)
    pyautogui.mouseUp()

# Draw a new card from the stack
stackX = 1321
stackY = 484
def drawNewCard():
    pyautogui.moveTo(stackX, stackY)
    pyautogui.click()

# Move to the top card of stack
topX = 1416
topY = 366
def moveToTop():
    pyautogui.moveTo(topX, topY)

# Collect top card
def collectTop():
    moveToTop()
    pyautogui.doubleClick()