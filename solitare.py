from time import sleep
import cardIdentifier
import inputManager
import pyautogui

# The minimum number a card must be to be placed from the stack.
STACK_MIN = 4

# Max gap of the highest and lowest ace
# This is ignored if the card is below a mystery card.
MAX_GAP = 3

# Number of out-of-place kings found.
queuedKings = 0

# Represents the top stack, ace piles, and tableau
stack: cardIdentifier.Card = None
aces = [cardIdentifier.Card(-1,0), cardIdentifier.Card(-1,0), cardIdentifier.Card(-1,0), cardIdentifier.Card(-1,0)]
game = [[None], [None], [None], [None], [None], [None], [None]]

# Keep track of whether or not stack was drawn from in cycle. If not, then game is in a loop.
stackDrawn = False

# Keep track if first loop occurred
firstLoop = False

# Keep track of gap size
curGap = MAX_GAP

# Determine if a new stack card should be chosen
drawStack = False

#Adds one to queuedKings if card is a king, otherwise does nothing
def addKing(king: cardIdentifier.Card):
    global queuedKings
    queuedKings += 1 if king.value == 13 else 0

# Get new card from stack
def newStack():
    #Draw card from stack.
    inputManager.drawNewCard()

    #Wait a bit so the stack can update before reading.
    sleep(0.4)

    #Read the top card
    global stack
    stack = cardIdentifier.getTopCard()

    #Add to kings
    if(not firstLoop):
        addKing(stack)

#Sets up the game as a regular solitare game. Reads currently available cards in tableau
#and adds them to game table accordingly.
#Also reads card from stack.
def initGame():
    #initiate the main game
    for col in range(0,7):
        fullColumn = []
        #add mystery cards
        for mystery in range(0,col):
            fullColumn.append(cardIdentifier.Card(-1, 0))

        foundCard = cardIdentifier.getCard(col,col)
        fullColumn.append(foundCard)
        game[col] = fullColumn

        #If the found card is a king and not in place, add to queued kings.
        if col > 0 and foundCard.value == 13:
            addKing(foundCard)

    newStack()


# Print the current tableau. For debugging.
def printGame():
    for col in game:
        for card in col:
            if card.value == 0:
                print("?", end="")
            else:
                print(card.printValue(), end="")
        print()
    print("Stack: {}".format(stack.printValue()))
    print("Aces: H: {}, S: {}, D: {}, C: {}".format(aces[0], aces[1], aces[2], aces[3]))
    print("Potential king cards: {}\n".format(str(queuedKings)))

def checkCards(a: cardIdentifier.Card, b: cardIdentifier.Card):
    #If a is one higher than b, and if they are different suits, then they are valid.
    if b.value + 1 == a.value and (a.suit % 2) != (b.suit % 2):
        return True
    return False

#Reads a card and applys information to program and game.
def readCard(bci, col, gColumn):
    #Read new card and update gColumn if not first card.
    if bci > 0:
        newCard = cardIdentifier.getCard(col, bci - 1)
        gColumn[bci - 1] = newCard
        addKing(newCard)

#Moves a card to a different column, and mirrors movement in-game.
#Also checks new card
def moveCard(col, checkCol, baseCardIndex, moveIndex):
    gColumn = game[col]
    checkColumn = game[checkCol]

    #First move in program.
    checkColumn.extend(gColumn[baseCardIndex:])
    del gColumn[baseCardIndex:]

    #Then move it in-game
    inputManager.moveToCard(col, baseCardIndex)
    #print("Moving to: {}, {}".format(checkCol, moveIndex))
    inputManager.dragTo(checkCol, moveIndex)


    #Read card
    print("Reading card in col {}, index {}".format(col, baseCardIndex))
    readCard(baseCardIndex, col, gColumn)

#Move a card from the [[CARD]] stack to one of the [[TABLEAU]] stacks.
def moveFromStack(col):
    gColumn = game[col]

    # Add card from stack to the column
    global stack
    gColumn.append(stack)

    # Apply move in game
    inputManager.moveToTop()
    inputManager.dragTo(col, len(gColumn) - 1)

    # Draw a new card from the stack, and update
    newStack()


#In greatest to least order, checks for cards with an empty slot
#maybe not g2l
#When a move is completed, restart the function.
def moveToStack():
    #Go through each column
    cont = True
    moved = False
    global queuedKings
    while(cont):
        cont = False
        for col in range(6,-1,-1):
            #Only proceed if column isn't empty
            if len(game[col]) > 0:
                #Find base card, which is the first known card after an unknown card.
                gColumn = game[col]
                baseCard = gColumn[0]
                baseCardIndex = 0
                #print(baseCard)
                #If first card is a mystery card, then the card below it can be moved.
                #If the first card is known and there is a king available, the card can be moved too.
                if baseCard.value <= 0 or queuedKings > 0:
                    #Keep going until card is found then
                    for mystCol, card in enumerate(gColumn):
                        if(card.value > 0):
                            baseCard = card
                            baseCardIndex = mystCol
                            break
                    #If the card is a MISPLACED king, see if there are empty spaces available.
                    #If not, proceed normally.
                    if baseCard.value == 13 and baseCardIndex > 0:
                        for checkCol in range(6,-1,-1):
                            if len(game[checkCol]) == 0:
                                #Move king to empty spot.
                                moveCard(col, checkCol, baseCardIndex, 0)

                                #Decrease queue by 1.
                                queuedKings -= 1

                                cont = True
                                moved = True
                                break
                    else:
                        #Now check other columns
                        for checkCol in range(6,-1,-1):
                            #Only proceed if checkCol isn't empty.
                            checkColumn = game[checkCol]

                            if len(checkColumn) > 0:
                                #Get last card
                                checkCard = checkColumn[len(checkColumn) - 1]
                                #Check if two cards match
                                if checkCards(checkCard, baseCard):
                                    #print("Moving {},{}:{} {},{}:{}".format(col, baseCardIndex, baseCard.value, checkCol, len(checkColumn), checkCard.value))
                                    #printGame()

                                    #Move card to other column.
                                    moveCard(col, checkCol, baseCardIndex, len(checkColumn))

                                    #Let program know another pass must happen
                                    cont = True
                                    moved = True
                                    break
    return moved

#Gets ace with least value
def getMinAce():
    min = 0
    for card in aces:
        if card != None:
            min = card.value if card.value < min else min
    return min


#Searches and collects cards for the ace piles.
#gap: the gap between cards that should be collected.
#Gap is usually MAX_GAP, but may be 13, which indicates vacuum mode.
def collectCards(gap):
    cont = True
    #exhaustion = 10
    while(cont):# and exhaustion > 0):
        cont = False
        for col in range(6,-1,-1):
            #Skip empties
            if(len(game[col]) > 0):
                gColumn = game[col]
                lci = len(gColumn) - 1
                lowestCard = gColumn[lci]

                #If the card is an ace, add it.
                #If not, add it if it's one greater.
                ace = aces[lowestCard.suit]
                if lowestCard.value == 1 or (ace != None and lowestCard.value == ace.value + 1 and lowestCard.value <= (getMinAce() + gap) ):
                    #Add in program
                    aces[lowestCard.suit] = lowestCard
                    del gColumn[-1]

                    #Apply in game
                    inputManager.moveToCard(col, lci)
                    inputManager.collectCard()

                    #Read new card
                    readCard(lci, col, gColumn)
                    cont = True
                    #exhaustion -= 1

# Given a card, checks to see if it can be placed in any of the columns.
# Returns the column that the card can be placed in
def canStackBePlaced():
    global stackDrawn
    #Check stack min first
    if stack.value >= STACK_MIN:
        for col in range(0, 7, 1):
            #Only proceed if column isn't empty
            if len(game[col]) > 0:
                #Find base card, in this case the bottommost card.
                gColumn = game[col]
                baseCardIndex = len(gColumn) - 1
                baseCard = gColumn[baseCardIndex]

                # If stack can be placed below baseCard, then the move will work.
                if checkCards(baseCard, stack):
                    stackDrawn = True 
                    return col
            # ..unless stack is a king
            elif stack.value == 13:
                stackDrawn = True
                return col
    return -1

# See if ace can go to any of the ace piles
def collectStack(stackCol):
    global stack
    global stackDrawn
    card = aces[stack.suit]
    placed = stackCol
    print("Stack: {} Ace: {}".format(stack.value, card.value))
    if card != None and stack.value - 1 == card.value:
        #Collect stack in-game
        print("Value: {}".format(stack.value))
        inputManager.collectTop()

        #Update aces and stack
        aces[stack.suit] = stack
        stack = cardIdentifier.getTopCard()
        addKing(stack)
        stackDrawn = True
        placed = -2
    return placed

# See if pile is empty
def isPileEmpty():
    pile = cardIdentifier.getTopPile()
    print(pile.value)
    return pile.value == -1

#Switch to game screen
pyautogui.hotkey('alt', 'tab')

#Initialize game first
initGame()
printGame()
passes = 200
stackchecks = 200

# For now, limit number of turns.
while(passes > 0 and stackchecks > 0):
    # Steps 1 & 2
    arrange = True
    while(arrange):
        collectCards(curGap)
        arrange = moveToStack()

    print("**BEGIN STACKING**")
    #Step 3
    stackCol = canStackBePlaced()
    while(stackCol == -1 and stackchecks > 0):
        # Get new stack
        if(drawStack):
            newStack()
            drawStack = False

        # See if new stack can be placed
        stackCol = canStackBePlaced()

        # See if stack can go to an ace pile
        stackCol = collectStack(stackCol)

        # Determine if inside loop at end of cycle
        if(isPileEmpty()):
            print("End of cycle.")
            print("Passes: {}".format(passes))
            # If no cards were drawn, then it is within a loop.
            if(stackDrawn == False):
                #Vaccuum mode!
                print("Loop detected!!!")
                
                #If it is already in vacuumm mode and it loses, then game over.
                if(curGap == 13):
                    passes = 0
                    stackchecks = 0
                curGap = 13

                #Keep track if first loop has occured
                firstLoop = True

                #Bypass the stack loop
                stackCol = -2
                
            #Draw from stack again!
            drawStack = True
            
            stackDrawn = False
        
        if(stackCol == -1):
            drawStack = True

        stackchecks -= 1
    if stackCol > -1:
        moveFromStack(stackCol)
    
    #Step 4 (auto)
    passes -= 1
    printGame()

#Close out and print
pyautogui.hotkey('alt', 'tab')
printGame()

if(passes <= 0):
    print("Passes exhausted! {} {}".format(passes, stackchecks))

if(stackchecks <= 0):
    print("Stack exhausted! {} {}".format(passes, stackchecks))

# The strategy:
# 1. First, all collectible cards will be placed in the ace pile.
# 2. Second, all stacks will be merged together.
# 2a. Additionally, kings will fill empty spots this step.
# 3. Next, cards from the stack will be drawn. If a card is placeable and greater/equal to
# STACK_MIN, then the card will be placed. Otherwise, another card will be drawn.
# 4. After being placed, repeat.
# 5. If stack is cycled and no cards can be placed, then vacuum mode is entered until unknown cards
# are found.
# 
# Vacuum mode currently just moves all cards to the ace pile regardless of the gap, but will
# probably make space + move cards off of mystery to different piles.