'''
Contains the Ship and Board classes
'''

class Ship():
    '''This class is used to store ship instances and the key properties for their handling.
    
    Attributes:
        length          The length of a ship measured by the board's blocks
        vertical        Defines the orientation of the ship
        placed          Registers if ship has been placed on the board by the user
        locations       Stores the coordinates of the placed ships' blocks
        hit_blocks      Same as above, but for blocks that have been hit by a missile

    Methods:
        len             Identifies length of a ship instance with the length attribute
        rotate          Switches the vertical boolean attribute
        check_if_sunk   Checks if all blocks of a given shit have been hit
    '''
    def __init__(self, length):
        self.length = length
        self.vertical = True
        self.placed = False
        self.locations = []
        self.hit_blocks = []
    def __len__(self):
        return self.length
    def rotate(self):
        self.vertical = not self.vertical
    def check_if_sunk(self):
        return set(self.locations) == set(self.hit_blocks)

class BoardState():
    '''Stores data regarding the ships positions on the user's boards

    Attributes:
        state           A 10x10 grid that stores the ship's positions on the user's board
                        based on the coordinates
        guess_state     Same as above but for the user's guesses regarding the opponent's fleet
        placed_ships    Stores all instances of ships that have been placed on the board
        sunk_ships      Same as above but for ships which have been sunk

    Methods:
        show                Prints the user's own board state; mainly used for testing
        get_surroundings    For any given block, it will return a set of coordinates
                            within the board where ships can no longer be placed
    '''
    def __init__(self):
        self.state = [[" "]*10,[" "]*10,[" "]*10,[" "]*10,[" "]*10,
                      [" "]*10,[" "]*10,[" "]*10,[" "]*10,[" "]*10]
        self.guess_state = [[" "]*10,[" "]*10,[" "]*10,[" "]*10,[" "]*10,
                            [" "]*10,[" "]*10,[" "]*10,[" "]*10,[" "]*10]
        self.placed_ships = []
        self.sunk_ships = []
    def show(self):
        for i in range(10):
            print(self.state[i])
    def get_surroundings(self, row, col):
        '''
        Returns a block's surroundings based on its coordinates

        Input:
            row         Concerning the vertical position of the block
            column      Concerning the horizontal position of the block

        Output:
            surroundings    A set of tuples containing the coordinates of
                            neighbouring blocks
        '''
        surroundings = set()
        for i in range(-1,2):
            if (row + i) in range(10):
                for j in range(-1,2):
                    if (col + j) in range(10) and not {i,j}.issubset({0}):
                        # Exclude the central block from the list of neighbouring blocks
                        # and add the rest to the 'surroundings' set
                        surroundings.add((row+i, col+j))
        return surroundings