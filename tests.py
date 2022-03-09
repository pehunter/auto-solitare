import logging
import unittest
import pyautogui
import cardIdentifier
import inputManager

class IdentifierTest(unittest.TestCase):
    #Switch to card view before testing

    def test_firstCard(self):
        firstCard = cardIdentifier.getCard(0,0)
        self.assertNotEqual(firstCard.value, 0)

    def test_secondcard(self):
        secondCard = cardIdentifier.getCard(1,1)
        self.assertNotEqual(secondCard.value, 0)

    def test_fourthcard(self):
        fourthCard = cardIdentifier.getCard(3,3)
        self.assertNotEqual(fourthCard.value, 0)
    
    def test_allcards(self):
        for i in range(0, 7):
            card = cardIdentifier.getCard(i, i)
            self.assertNotEqual(card.value, 0)
            print(card)
    
    def test_topCard(self):
        top = cardIdentifier.getTopCard()
        self.assertNotEqual(top.value, 0)

    def test_topPile(self):
        pile = cardIdentifier.getTopPile()
        self.assertEqual(pile.value, 0)

class MouseTest(unittest.TestCase):
    def test_moveMouseFirst(self):
        inputManager.moveToCard(0,0)
        self.assertEqual(pyautogui.position(), inputManager.getLocation(0,0, inputManager.sizeX*2, inputManager.sizeY/2))

    def test_moveMouseSeven(self):
        inputManager.moveToCard(6,6)
        self.assertEqual(pyautogui.position(), inputManager.getLocation(6,6, inputManager.sizeX*2, inputManager.sizeY/2))

    def test_moveMouseBlank(self):
        inputManager.moveToCard(1, 13)
        self.assertEqual(pyautogui.position(), inputManager.getLocation(1, 13, inputManager.sizeX*2, inputManager.sizeY/2))
    
    # Can't really programatically verify so must use Brain
    @unittest.skip("Messes with other tests so no")
    def test_collectFirst(self):
        inputManager.moveToCard(1,1)
        inputManager.collectCard()
        self.assertTrue(True)

    @unittest.skip("Gl verifying this")
    def test_goToAce(self):
        inputManager.moveToAce(3)
        self.assertTrue(True)

    @unittest.skip("Again dont do it")
    def test_moveCard(self):
        inputManager.moveToCard(5,5)
        inputManager.dragTo(1,1)
        card = cardIdentifier.getCard(1,2)
        self.assertEqual(card.value, 7)
    
    def test_drawNew(self):
        inputManager.drawNewCard()
        card = cardIdentifier.getTopCard()
        self.assertNotEqual(card.value, 0)

def suite1():
    suit = unittest.TestSuite() 
    suit.addTest(MouseTest("test_moveMouseFirst"))
    suit.addTest(MouseTest("test_moveMouseSeven"))
    suit.addTest(MouseTest("test_moveMouseBlank"))
    suit.addTest(MouseTest("test_drawNew"))
    return suit

def suite2():
    suite = unittest.TestSuite()
    suite.addTest(IdentifierTest("test_firstCard"))
    suite.addTest(IdentifierTest("test_secondcard"))
    suite.addTest(IdentifierTest("test_fourthcard"))
    suite.addTest(IdentifierTest("test_allcards"))
    suite.addTest(IdentifierTest("test_topCard"))
    suite.addTest(IdentifierTest("test_topPile"))
    return suite

def testSuite():
    suite = unittest.TestSuite()
    suite.addTest(MouseTest("test_goToAce"))
    return suite

if __name__ == '__main__':
    pyautogui.hotkey('alt', 'tab')
    runner = unittest.TextTestRunner()
    runner.run(suite2())
    pyautogui.hotkey('alt', 'tab')