'''
Contains the CPU class
'''

from random import randint
from board_class import Ship, BoardState

class CPU():
    '''This class is used to define the actions of the CPU in a game vs a player

    Attributes:
        ship_lengths            Same as in the Player class
        board                   The CPU also has two boards
        num_of_tries            Number of fired bullets/canonballs
        discarded blocks        Used as part of the algorithm that looks for the player's
                                ships. It stores the coordinates where the enemy fleet cannot be located.
        currently_hit_ship      Stores the ship instance that is currently being scanned to be sunk
        current_scanned_coord   Last coordinates the ship fired upon
        available_squares       Stores the remaining squares where the CPU can fire

    Methods:
        place_ships             Takes random coordinates and orientation for each ship
                                until the CPU has placed all 10 ships on its board.
    '''
    ship_lengths = [
                    4,
                    3,3,
                    2,2,2,
                    1,1,1,1
                    ]
    def __init__(self):
        self.board = BoardState()
        self.num_of_tries = 0
        self.discarded_blocks = set()
        self.currently_hit_ship = '' # Takes a dummy variably upon initialisation
        self.current_scanned_coord = ()
        self.available_squares = []
    def place_ships(self):
        ''' Plants the CPU's ships across the board in a random fashion.

        Input: -

        Output: self.board
        '''
        # Run until all ships have been placed, i.e., until ship_lengths is empty after
        # popping all of its elements.
        while len(self.ship_lengths) > 0:
            ship = Ship(self.ship_lengths[0]) # Create the ship instance based on the ship's block length
            rot_times = randint(1,10)
            if rot_times % 2 == 1:
            # Give a random orientation
                ship.rotate()

            # Take a random position
            pos_x = randint(0,9)
            pos_y = randint(0,9)
            # Store the initial position
            initial_pos_x, initial_pos_y = pos_x, pos_y
            # Get the whole ship's surroundings block by block
            coord_surroundings = set()
            for block in range(len(ship)):
                for i in range(-1,2):
                    if (pos_x + i) in range(10):
                        for j in range(-1,2):
                            if (pos_y + j) in range(10):
                                coord_surroundings.add(self.board.state[pos_x+i][pos_y+j])
                if ship.vertical:
                    pos_y += 1
                else:
                    pos_x += 1

            # If the given position satisfies all the game's rules, place the ship; else, try again
            if 'X' not in coord_surroundings and {pos_x-1, pos_y-1}.issubset(set(range(10))):
                # Restore original position
                pos_x, pos_y = initial_pos_x, initial_pos_y
                # Mark each block's position with an 'X' in the CPU's board's state
                for block in range(len(ship)):
                    self.board.state[pos_x][pos_y] = 'X'
                    ship.locations.append((pos_x, pos_y))
                    if ship.vertical:
                        pos_y += 1
                    else:
                        pos_x += 1

                # Store the placed ship, delete the current ship length, and move on to the next
                self.board.placed_ships.append(ship)
                self.ship_lengths.pop(0)
            else:
                continue

        return self.board