#Importing packages
import random
import os
import time
import colorama
try: #Checks for the existance of the colorama library
	from colorama import Fore, Back, Style
	colorama.init()
except:
	print("Missing Dependency: Colorama. Please install the most recent version of colorama")
	quit()

#I do not want to constantly write os.system("cls" if os.name == "nt" else "clear")
def clear():
	os.system("cls" if os.name == "nt" else "clear")
#Defining the Cards class and defining each card, creating the deck and hands, ImmageMiddle is used for the Card images
deck = []
middle = []
players = []
validNum = []
playerWinList = []
class Card():
        def __init__(self, suit, number, imageMiddle):
                self.suit = suit
                self.number = number
                self.imageMiddle = imageMiddle
                deck.append(self)
#Defining the Players class, these will be defined later. Hand is an list that is used as the hand
class Player():
	def __init__(self, hand, id):									
		self.hand = hand
		self.id = id
		players.append(self)

suits = ["♥ Hearts", "♦ Diamonds", "♠ Spades", "♣ Clubs"]
ranks = {6: " 6", 7: " 7", 8: " 8", 9: " 9", 10: "10", 11: " J", 12: " Q", 13: " K", 14: " A"}

deck = [Card(suit, rank, f"│{suit[0]}{face}│") for suit in suits for rank, face in ranks.items()]

#The Decks shuffled, hands given
random.shuffle(deck)
trumpsuit = deck[0].suit

def durak():
    global playerAmount
    playerAmount = 0

    # Player Amount input: Continues the loop if an invalid amount of players is given, or if an exception would occur. 
    # "quit" is used because Ctrl-C is accesible during this loop.
    # The quit command is case-INsensitive

    while playerAmount < 2 or playerAmount > 6:
        clear()
        print(Fore.RED + "D U R A K\n")
        print(Fore.YELLOW + "Python Edition\n")
        try:
            playerAmount = input(Fore.GREEN + "Amount of Players (2 - 6 or quit): ")
            if playerAmount.lower() == "quit":
                playerAmount = "quit"    
                break
            else:
                playerAmount = int(playerAmount)
        except KeyboardInterrupt:
            quit()
        except:
            clear()
            playerAmount = 0
            continue
    if playerAmount == "quit":
            quit()
    #Defining Players. The loop gives each player 6 cards.

    for i in range(playerAmount):
        Player([], i+1)
        for j in range(6):
            players[i].hand.append(deck[0])
            deck.pop(0)
            playerIndex = 0
    while len(players) > 1:
            turn(players[playerIndex])
            if len(deck) > 0:
                    print(Fore.GREEN + "Each player takes cards until they have 6 cards or the deck runs out")
                    for player in players:
                            while len(player.hand) < 6:
                                    player.hand.append(deck[0])
                                    deck.pop(0)
                                    if len(deck) == 0:
                                            print(Fore.RED + "The deck ran out")
                                            break
            else:
                    print(Fore.RED + "There are no more cards in the deck")
            time.sleep(3)
            if playerIndex == len(players) - 1:
                    playerIndex = 0
            else:
                    playerIndex += 1
    playerWinList.append(players[0])
    clear()

    for player in playerWinList:
            if playerWinList.index(player) == 0:
                    print(Fore.YELLOW + f"1st Place: Player {player.id}")
            elif playerWinList.index(player) == 1:
                    print(Fore.WHITE + f"2nd Place: Player {player.id}")
            elif playerWinList.index(player) == 2:
                    print(Fore.YELLOW + Style.DIM + f"3rd Place: Player {player.id}")
            else:
                    print(Fore.RED + f"1st Place: Player {player.id}")

# This Command displays cards using the imageMiddle attribute
def dispDeck(arr, linelen, checkType="none", arrc=[]):
    iteration = 1
    while iteration < arr.__len__() // linelen + 2:
        j = linelen * iteration - linelen + 1
        if arr.__len__() < iteration * linelen:
            diff = linelen - arr.__len__() % linelen            
        else:   
            diff = 0            
        
        # Top border of cards
        while j < linelen * iteration + 1 - diff:
            print(Fore.WHITE + "┌───┐", end="     ")
            j += 1
        print("")

        # Middle part with suit and rank
        j = linelen * iteration - linelen + 1
        while j < linelen * iteration - diff + 1:
            print(Fore.WHITE + arr[j - 1].imageMiddle, end="     ")
            j += 1
        print("")

        # Bottom border of cards
        j = linelen * iteration - linelen + 1
        while j < linelen * iteration - diff + 1:
            print("└───┘", end="     ")
            j += 1
        print("")

        # Aligned numeration for each check type
        if checkType == "numerate":
            j = linelen * iteration - linelen + 1
            while j < linelen * iteration - diff + 1:
                if j < 10:
                    print(Fore.GREEN + f"( {j} )", end="     ")  # Single digit indices
                else:
                    print(Fore.GREEN + f"({j} )", end="     ")  # Double digit indices
                j += 1
            print("")

        elif checkType == "attack":
            j = linelen * iteration - linelen + 1
            while j < linelen * iteration - diff + 1:
                # Check if card's number is in validNum list (playable)
                if arr[j - 1].number in validNum:
                    if j < 10:
                        print(Fore.GREEN + f"( {j} )", end="     ")  # Single digit indices
                    else:
                        print(Fore.GREEN + f"({j} )", end="     ")  # Double digit indices
                else:
                    print(Fore.RED + "( X )", end="     ")  # Unplayable card
                j += 1
            print("")

        elif checkType == "defend":
            j = linelen * iteration - linelen + 1
            while j < linelen * iteration - diff + 1:
                # Check if card is a valid defending card
                if arr[j - 1].suit == trumpsuit and arrc[-1].suit != trumpsuit:
                    if j < 10:
                        print(Fore.GREEN + f"( {j} )", end="     ")
                    else:
                        print(Fore.GREEN + f"({j} )", end="     ")
                elif arr[j - 1].number > arrc[-1].number and arr[j - 1].suit == arrc[-1].suit:
                    if j < 10:
                        print(Fore.GREEN + f"( {j} )", end="     ")
                    else:
                        print(Fore.GREEN + f"({j} )", end="     ")
                else:
                    print(Fore.RED + "( X )", end="     ")  # Unplayable card
                j += 1
            print("")

        iteration += 1


# firstattack is similar to the attack function, except that one isn't able to pass. 
def firstAttack(attacker):
	clear()
	input(Fore.GREEN + f"Player {attacker.id} ready?")
	clear()
	print(Fore.GREEN + "Middle:")
	dispDeck(middle, 2)
	print("\n")
	print(Fore.GREEN + "Your Hand: ")
	dispDeck(attacker.hand, 5, "numerate")
	print("\n")
	print(Fore.GREEN + f"Trump Suit: {trumpsuit}")
	inInt = 0
	while inInt < 1 or inInt > len(attacker.hand):
		inInt = input(Fore.GREEN + f"Play any Card (1 - {len(attacker.hand)}): ")
		try: 
			inInt = int(inInt)
		except:
			inInt = 0
			continue
	middle.append(attacker.hand[inInt - 1])
	validNum.append(attacker.hand[inInt - 1].number)
	attacker.hand.pop(inInt -1)

# Defense Input doesn't let people play cards that are not of the same suit or of the trump suit and are lower value, passing results in taking all cards
def defense(defender):
	clear()
	input(Fore.GREEN + f"Player {defender.id} ready?")
	clear()
	print(Fore.GREEN + "Middle:")
	dispDeck(middle, 2)
	print("\n")
	print(Fore.GREEN + "Your Hand: ")
	dispDeck(defender.hand, 5, "defend", middle)
	print("\n")
	print(Fore.GREEN + f"Trump Suit: {trumpsuit}")
	inInt = 0
	playable = False
	while inInt != "pass" and not playable or inInt < 1 or inInt > len(defender.hand):
		inInt = input(Fore.GREEN + f"Defend this card (1 - {len(defender.hand)} or pass): ")
		if inInt.lower() == "pass":
			inInt = "pass"
			break
		else:
			try:
				inInt = int(inInt)
				if defender.hand[inInt - 1].number > middle[-1].number and defender.hand[inInt - 1].suit == middle[-1].suit:
					playable = True
				elif defender.hand[inInt - 1].suit == trumpsuit and middle[-1].suit != trumpsuit:
					playable = True
				else:
					continue
			except:
				inInt = 0
				continue
	if inInt == "pass":
		input(Fore.RED + "You take all cards (Press Enter)")
		for element in middle:
			defender.hand.append(element)
		del middle[:]
		return "fail"
	middle.append(defender.hand[inInt - 1])
	validNum.append(defender.hand[inInt - 1].number)
	defender.hand.pop(inInt - 1)
		

# attack input doesn't let people play cards of values that haven't been played
def attack(attacker):
	clear()
	input(Fore.GREEN + f"Player {attacker.id} ready?")
	clear()
	print(Fore.GREEN + "Middle:")
	dispDeck(middle, 2)
	print("\n")
	print(Fore.GREEN + "Your Hand: ")
	dispDeck(attacker.hand, 5, "attack", middle)
	print("\n")
	print(Fore.GREEN + f"Trump Suit: {trumpsuit}")
	inInt = 0
	playable = False
	while inInt != "pass" and not playable or inInt < 1 or inInt > len(attacker.hand):
		inInt = input(Fore.GREEN + f"Play any Card or pass (1 - {len(attacker.hand)} or pass): ")
		if inInt.lower() == "pass":
			inInt = "pass"
			break
		else:
			try: 
				inInt = int(inInt)
				if attacker.hand[inInt - 1].number in validNum:
					playable = True
			except:
				inInt = 0
				continue
	if inInt == "pass":
		return "pass"
	middle.append(attacker.hand[inInt - 1])
	validNum.append(attacker.hand[inInt - 1].number)
	attacker.hand.pop(inInt -1)
	return "attacked"


# Checkwins checks if any player no longer has cards, resulting in a victory
def checkWins():
	for p in players:
		if len(p.hand) == 0:
			print(Fore.YELLOW + f"Player {player.id} no longer has any cards")
			playerWinList.append(p)
			players.pop(players.index(p))

# turn requires a firstPlayer object. The First player attacks first, and the next player defends. afterwards, the attackers may attack 5 times, pass changes the attacker to the next player in the list.
# If the defender defends 6 times, or each attacker has passed, the played cards get discarded by emptying the middle list	
def turn(firstPlayer):
	if players.index(firstPlayer) + 1 < len(players):
		defender = players[players.index(firstPlayer) + 1]
	else:
		defender = players[0]
	attacker = firstPlayer
	firstAttack(attacker)
	checkWins()
	defResult = defense(defender)
	if defResult == "fail":
		return
	checkWins()
	for trick in range(5):
		attResult = ""
		while attResult != "attacked":
			attResult = attack(attacker)
			passCount = 0
			if attResult == "pass": 
				passCount += 1
				if passCount >= len(players) - 1:
					print(Fore.RED + "All Cards get discarded")
					del middle[:]
					
					time.sleep(1)
					clear()
					return
				if attacker.id + 1 == defender.id:
					if attacker.id + 2 > len(players):
						if defender.id == 1:
							attacker = players[1]
						else:
							attacker = players[0]
					else:
						attacker = players[players.index(attacker) + 2]
				else:
					if attacker.id + 1 > len(players):
						if defender.id == 1:
							attacker = players[1]
						else:
							attacker = players[0]
					else:
						attacker = players[players.index(attacker) + 1]
		checkWins()
		defResult = defense(defender)
		if defResult == "fail":
			return
		checkWins()
	print(Fore.RED + "All Cards get discarded")
	checkWins()
	del middle[:]
	time.sleep(3)
	clear()
	return


if __name__ == "__main__":
        durak()