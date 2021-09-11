'''
Contains the Player class
'''

from board_class import Ship, BoardState

class Player():
    '''This class is used to store the data of all human players participating in the game

    Attributes:
        ship_lengths    The number of ships and their length in this variation of the game
        name            Username of the player
        board           Each player has his/her own two boards; one for placing and one for guessing
        placing_ships   Checks if the player is done placing ships in order to start the guessing game
        num_of_tries    Number of fired bullets/canonballs
    '''
    ship_lengths = [
                    4,
                    3,3,
                    2,2,2,
                    1,1,1,1
                    ]
    def __init__(self, name):
        self.name = name
        self.board = BoardState()
        self.placing_ships = True
        self.num_of_tries = 0
        self.discarded_blocks = set() # Unused. Simplifies code in main.py since we can call 
                                      # user.discarded_blocks for both types of users (Player and CPU).