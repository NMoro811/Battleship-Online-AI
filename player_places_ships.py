'''
This module is executed when a player is placing their ships on the board. Hence, the main goal
is to update the Player's Board state given the player's choices,  while ensuring these are in
accordance with the game's rules.
'''

# EXTERNAL MODULES
import os
import pygame as game
from numpy import array, cos, sin, deg2rad 
from random import randint
from copy import deepcopy
from string import ascii_uppercase

# INTERNAL MODULES
from board_class import Ship, BoardState
from cpu_class import CPU
from player_class import Player

# GLOBAL VARIABLES
board_width = board_height = 512 # Board's sizes
dimension = 10
sq_size = board_height // dimension
square_list = [] # List of all the board's squares
width = height = 712 # Window's dimensions
# Used for displaying each row's or column's letter/number (inspired by Lichess boards)
alpha = ascii_uppercase
letter_dict = {index: letter for index, letter in enumerate(alpha)}
number_dict = {index: index+1 for index in range(dimension)}

# Load background picture
background = game.image.load(os.path.join("img", "background3.jpg"))

def ship_placing(name):
	''' Main function of the module

	Input: Player's name (from the menu window)

	Output: (Updated) player instance
	'''
	# Create player instance
	player = Player(name)
	player.board = BoardState()
	game.init()

	# Set up the game's fonts and display
	game_font = game.font.SysFont('Cambria',20)
	square_font = game.font.SysFont('Cambria',14)
	screen = game.display.set_mode((width, height))
	# Limit the number of events to improve efficiency
	game.event.set_allowed([game.QUIT, game.MOUSEBUTTONDOWN, game.MOUSEBUTTONUP, game.MOUSEMOTION, game.KEYDOWN])

	# Sets up the 'Ready' button, which is displayed only after all ships have been
	# preliminarly placed on the board.
	mouse_on_ready_button = False # Used to higlight the 'Ready button'
	button_font = game.font.SysFont('Cambria',26)
	ready_button = game.Rect(540, 200, sq_size*2.25, sq_size*1.5)

	player_ready = False # Activated after pressing the 'Ready' button, confirming the fleet's layout
	dragging_states = [] # Stores the booleans that check whether each ship is being grabbed
	surroundings_list = ['', '', '', '', '', '', '', '', '', ''] # To be filled with each ship's surroundings
	list_of_ships = [] # To store all the placed ships
	original_list_of_ships = [] # Stores all the ships' original positions, i.e., below the board
	index_dict = {0: 1, 1: 1, 2: 1, 3: 1,
				4: 2, 5: 2, 6: 2,
				7: 3, 8: 3,
				9: 4} # Relates indices in range(10) to the ships' lengths

	# Will only stop if the player quits or if all ships have been placed and the 'Ready' button has been pressed
	while player.placing_ships:

		# Stores all the ship surroundings that are not empty strings
		placed_ships_surroundings = [surroundings for surroundings in surroundings_list if type(surroundings) != str]

		# Execute after the 'Ready' button has been pressed, updating the Player instance accordingly
		if player_ready:
			for ship_rect in list_of_ships:
				# Creates a Ship instance corresponding to a ship on the board
				ship_dimensions = {ship_rect.width // sq_size, ship_rect.height // sq_size}
				ship_instance = Ship(max(ship_dimensions))
				# Store the created Ship instance
				player.board.placed_ships.append(ship_instance)
				topleft_x, topleft_y = ship_rect.topleft
				# Place an 'X' wherever a ship's block is present on the board
				first_square = mouse_on_square(topleft_x, topleft_y)
				row, col = first_square
				for i in range(len(ship_instance)):
					ship_instance.locations.append((row,col))
					player.board.state[row][col] = 'X'
					if (ship_rect.height // sq_size) < (ship_rect.width // sq_size):
						# Easy way to check if ship is horizontal
						col += 1
					else:
						row += 1
				if (ship_rect.height // sq_size) < (ship_rect.width // sq_size):
					ship_instance.vertical = False # Ship is horizontal; updates the 'vertical' attribute
			
			# Break the enclosing loop; all the ships have been placed		
			player.placing_ships = False
			break

		# To be updated every frame
		player.board.state = [[" "]*10,[" "]*10,[" "]*10,[" "]*10,[" "]*10,
                      			[" "]*10,[" "]*10,[" "]*10,[" "]*10,[" "]*10]
        # Display background
		screen.blit(background, (0, 0))
		# Create a rectangle with the board's dimensions
		blank_board = game.Rect(0, 0,board_width, board_height)

		# 'Ready?' button - appears only when the 10 ships have been placed on the board
		if len(placed_ships_surroundings) == 10:
			if not mouse_on_ready_button:
				ready_text = button_font.render('Ready!', False, (255, 255, 255))
				game.draw.rect(screen, (0, 165, 208), ready_button)
				screen.blit(ready_text, (540+sq_size*0.4, 200+sq_size*0.43))
			else:
				ready_text = button_font.render('Ready!', False, (0, 165, 208))
				game.draw.rect(screen, (255, 255, 255), ready_button)
				screen.blit(ready_text, (540+sq_size*0.4, 200+sq_size*0.43))

		mouse_x, mouse_y = game.mouse.get_pos()
		
		# EVENT HANDLING
		for e in game.event.get():
			if e.type == game.QUIT:
				player.placing_ships = False
			if e.type == game.MOUSEBUTTONDOWN:
				mouse_x, mouse_y = e.pos
				# LEFT click
				if e.button == 1:
					# If clicked on a ship, drag it with the mouse around the screen
					for rect_len in range(10):
						if list_of_ships[rect_len].collidepoint(e.pos):
							rect = list_of_ships[rect_len]
							# Store original position and orientation -- (might change later)
							rect_original_x, rect_original_y, rect_original_width, rect_original_height = (rect.x, rect.y, rect.width, rect.height)
							# Re-establish ship surroundings and draggin boolean while being grabbed
							surroundings_list[rect_len] = ''
							dragging_states[rect_len] = True
							# Store position offset
							offset_x = rect.x - mouse_x
							offset_y = rect.y - mouse_y
							break
					else:
						# User presses 'Ready' button
						if mouse_on_ready_button:
							player_ready = True
				elif e.button == 3:
					# RIGHT click
					for rect_len in range(10):
						# If clicked on a ship, return to its initial position below the board
						if list_of_ships[rect_len].collidepoint(e.pos):
							rect = list_of_ships[rect_len]
							original_rect = original_list_of_ships[rect_len]
							rect.update(original_rect.x, original_rect.y, original_rect.width, original_rect.height)
							surroundings_list[rect_len] = ''
							break

			if e.type == game.MOUSEBUTTONUP:
				# If dragging one of the ships and stopped pressing button, place the ship there
				# unless it is out of the board or against the rules
				if e.button == 1 and True in dragging_states:
					dragging_states[rect_len] = False
					row = mouse_on_square(mouse_x, mouse_y)[0]
					col = mouse_on_square(mouse_x, mouse_y)[1]
					# If ship is wholly contained on the board -- (might change later)
					if blank_board.contains(rect):
						ship_square_x = (-offset_x // sq_size)
						ship_square_y = (-offset_y // sq_size)
						intended_position = game.Rect((col-ship_square_x)*sq_size, (row-ship_square_y)*sq_size, rect.width, rect.height)
						# If the intended position of the released ship is not in any other ship's surroundings, place
						if intended_position.collidelist(placed_ships_surroundings) == -1:
							rect.update((col-ship_square_x)*sq_size, (row-ship_square_y)*sq_size, rect.width, rect.height)
							surroundings = rect.copy()
							surroundings = surroundings.inflate(sq_size*2, sq_size*2)
							surroundings_list[rect_len] = surroundings
						# Else, return to original position
						else:
							rect.x, rect.y, rect.width, rect.height = (rect_original_x, rect_original_y, rect_original_width, rect_original_height)
					# Return to original position
					else:
						rect.x, rect.y, rect.width, rect.height = (rect_original_x, rect_original_y, rect_original_width, rect_original_height)

			if e.type == game.MOUSEMOTION:
				mouse_x, mouse_y = e.pos
				# If dragging a ship, move it with the mouse while mantaining size and orientation
				if True in dragging_states:
					rect.x = mouse_x + offset_x
					rect.y = mouse_y + offset_y
				# Else, if all ships have been placed, check if the mouse is on the 'Ready' button
				elif len(placed_ships_surroundings) == 10:
					if ready_button.collidepoint((mouse_x, mouse_y)):
						mouse_on_ready_button = True
					else:
						mouse_on_ready_button = False

			if e.type == game.KEYDOWN:
				if True in dragging_states:
					# Rotate the ship that is being dragged around the screen
					if e.key == game.K_LEFT or e.key == game.K_a or e.key == game.K_RIGHT or e.key == game.K_d:
						offset_x, offset_y = (offset_y, offset_x)
						# Find the ship that is being dragged
						for i in range(10):
							if dragging_states[i]:
								ship = list_of_ships[i]
								break
						# Rotate
						if e.key == game.K_RIGHT or e.key == game.K_d:
							angle = 90
						elif e.key == game.K_LEFT or e.key == game.K_a:
							angle = -90
						rotate_clockwise(ship,angle)
						# Update position after rotation
						mouse_x, mouse_y = game.mouse.get_pos()
						rect.x = mouse_x + offset_x
						rect.y = mouse_y + offset_y

		colors = [(0, 105, 148), game.Color("cyan"), game.Color("black")]
		global square_list
		# Store all the 100 squares on the board if it has not been done yet
		if len(square_list) == 0:
			square_list = collect_squares(square_list)
		# Place an 'X' on the user's board wherever there is a ship's block on the board
		detect_ships_on_board(player)

		# Print a grey bar below the board, where the ships are displaced, if not all have been placed
		if len(placed_ships_surroundings) < 10:
			game.draw.rect(screen, (64,65,66), game.Rect(0*sq_size, 10*sq_size, width, height-10*sq_size))

		# Execute only once; create every ship's rectangle, place them below the board for display, and
		# store their data in the relevant lists
		if len(dragging_states) < 10:
			coords_unplaced_ships = []
			num = 1
			while num <= 4:
				# Ships of this length that still need to be placed
				available_ships = len([n for n in player.ship_lengths if n == num])
				# Place them on the grey board
				if available_ships > 0:
					if num in {3,4}:
						coord_x = 2*sq_size
					else:
						coord_x = 8*sq_size
					if num in {2,4}:
						coord_y = 10.5*sq_size
					else:
						coord_y = 12.5*sq_size

					# Create and store the ship's rectangle
					ship_rect = game.Rect(coord_x, coord_y, num*sq_size, sq_size)
					list_of_ships.append(ship_rect)

					# Used for displaying available ships in show_available_ships
					coords_unplaced_ships.append((coord_x, coord_y))

					# Create copies of each kind of ship, place them in the same location
					for i in range (5-num):
						if i != 0:
							list_of_ships.append(ship_rect.copy())
						# Fill dragging_states
						ship_dragging = False
						dragging_states.append(ship_dragging)
				num += 1
				# Create a deep copy of list_of_ships to access original locations and orientations
				# of the ships more easily
				original_list_of_ships = deepcopy(list_of_ships)

		# Display the board
		draw_board(screen, colors, square_list, letter_dict, number_dict, square_font)

		mouse_x, mouse_y = game.mouse.get_pos()
		# Create tiny invisible square around the mouse so we can use collidelist instead
		# of collidepoint inside a 'for' loop
		tiny_sq_around_mouse = game.Rect(mouse_x, mouse_y, 0.001*sq_size, 0.001*sq_size)
		row = mouse_on_square(mouse_x, mouse_y)[0]
		col = mouse_on_square(mouse_x, mouse_y)[1]
		# Highlight the square the mouse is on as long as it does not collide with a ship or
		# a ship is being dragged. Note: further conditions inside the highlight_square func
		if row < 10 and col < 10:
			collide_indx = tiny_sq_around_mouse.collidelist(list_of_ships)
			if collide_indx == -1:
				highlight_square(screen, colors, mouse_x, mouse_y, placed_ships_surroundings, letter_dict, number_dict, square_font)
			elif not dragging_states[collide_indx]:
				highlight_square(screen, colors, mouse_x, mouse_y, placed_ships_surroundings, letter_dict, number_dict, square_font)

		# Display a count of the ships yet to be placed
		show_available_ships(screen, list_of_ships, original_list_of_ships, coords_unplaced_ships, index_dict)
		# Draw all ships and their surroundings -- Note: surroundings on top of background pic, will fix later
		for surroundings in surroundings_list:
			if type(surroundings) != str:
				game.draw.rect(screen, (59, 174, 254), surroundings)
		for ship in list_of_ships:
			game.draw.rect(screen, (111,67,42), ship)

		game.display.update()

	return player

# FUNCTIONS

def collect_squares(square_list):
	''' Store all the squares on the board

	Input: (empty) list of squares

	Output: updated list of squares
	'''
	for r in range(dimension):
		for c in range(dimension):
			square = game.Rect(c*sq_size, r*sq_size, sq_size, sq_size)
			square_list.append(square)
	return square_list

def draw_board(screen, colors, square_list, letter_dict, number_dict, square_font):
	''' Draw all the squares in square_list

	Input: screen, colors, square_list, letter_dict, number_dict, square_font

	Output: None
	'''
	for square in square_list:
		c = square.left // sq_size
		r = square.top // sq_size
		color = colors[((r+c)%2)]
		game.draw.rect(screen, color, square)

		# Choose color and letter corresponding to this row/column
		text_color = colors[((r+c-1)%2)]
		row_letter = letter_dict[r]
		col_number = number_dict[c]

		# Display on the board only for the squares in the first row or column
		row_text = square_font.render(f'{row_letter}', False, text_color)
		if c == 0:
			screen.blit(row_text, (square.topleft[0]+2, square.topleft[1]))

		col_text = square_font.render(f'{col_number}', False, text_color)
		if r== 0:
			screen.blit(col_text, (square.bottomright[0]-15, square.bottomright[1]-17.5))

def highlight_square(screen, colors, mouse_x, mouse_y, placed_ships_surroundings, letter_dict, number_dict, square_font):
	''' Create a highlighting visual effect on the square of the board the mouse is over

	Input: screen, colors, mouse_x, mouse_y, placed_ships_surroundings, letter_dict, number_dict, square_font

	Output: None
	'''
	# Create the square
	row = mouse_on_square(mouse_x, mouse_y)[0]
	col = mouse_on_square(mouse_x, mouse_y)[1]
	square = game.Rect(col*sq_size, row*sq_size, sq_size, sq_size)

	# Display numbers/letters
	text_color = colors[((row+col-1)%2)]
	row_letter = letter_dict[row]
	col_number = number_dict[col]

	row_text = square_font.render(f'{row_letter}', False, text_color)
	col_text = square_font.render(f'{col_number}', False, text_color)

	# Draw the square unless a ship or its surrounding has already been drawn there
	if square.collidelist(placed_ships_surroundings) == -1:
		# Draw squares
		color = colors[((row+col)%2)]
		# Draw a black square in place to create a shadowing effect
		game.draw.rect(screen, colors[2], square)
		# Different highlight effect on the last row/column to avoid it going out of the board
		if col < 9 and row < 9:
			game.draw.rect(screen, color, game.Rect(col*sq_size+2, row*sq_size+2, sq_size+2, sq_size+2))
		else:
			game.draw.rect(screen, color, game.Rect(col*sq_size+2, row*sq_size+2, sq_size, sq_size))
		# Coordinate letters/numbers also in highlighted text
		if col == 0:
			screen.blit(row_text, (square.topleft[0]+4, square.topleft[1]+2))
		if row == 0:
			screen.blit(col_text, (square.bottomright[0]-13, square.bottomright[1]-15.5))
	else:
		pass

def detect_ships_on_board(player):
	''' Place an 'X' on the player's board state wherever there is a ship's block on the board

	Input: Player instance

	Output: None
	'''
	for ship_instance in player.board.placed_ships:
		for coord in ship_instance.locations:
			r, c = coord
			player.board.state[r][c] = 'X'

def rotate_clockwise(rect, angle=0):
	''' Use a 2D rotational matrix to swap the orientation of the dragged ship

	Input: rect to be rotated, angle of rotation

	Output: None
	'''
	# To store the rotated coordinates of the chosen corners of the rect
	rotated_corner_list = []
	# From rad to deg
	a = deg2rad(angle)

	center_x, center_y = (rect.centerx, rect.centery)
	corner_list = [corner_1, corner_2] = (rect.topleft, rect.bottomleft)
	rotation_matrix = array([[cos(a), -sin(a)],[sin(a), cos(a)]])
	for corner in corner_list:
		# Set the origin at the rect's center
		corner = list(corner)
		corner[0] -= center_x
		corner[1] -= center_y
		# Rotate the 'centralised' coordinates
		rotated_corner = rotation_matrix.dot(array(corner).reshape(2,1))
		rotated_corner = [coord[0] for coord in rotated_corner]
		# Re-convert to the original 2D space
		rotated_corner[0] += center_x
		rotated_corner[1] += center_y

		# Store the coordinates as a tuple
		rotated_corner = tuple(rotated_corner)
		rotated_corner_list.append(rotated_corner)
	# Update the rect's orientation
	rect.update(rotated_corner[0], rotated_corner[1], rect.height, rect.width)

def show_available_ships(screen, list_of_ships, original_list_of_ships, coords_unplaced_ships, index_dict):
	''' Display the number of ships to be placed per category next to them

	Input: screen, list_of_ships, original_list_of_ships, coords_unplaced_ships, index_dict

	Output: None
	'''
	# Stores the number of available ships per type
	available_ships = [0,0,0,0]
	# Add +1 if the center of the original (unplaced) rect coincides with the current center
	for i in range(0,10):
		ship = list_of_ships[i]
		original_ship = original_list_of_ships[i]
		center_unplaced = (center_x, center_y) = (original_ship.centerx, original_ship.centery)
		if ship.collidepoint(center_unplaced):
			available_ships[index_dict[i]-1] += 1
	# Display the number next to the ship
	for j in range(0,4):
		if available_ships[j] > 0:
 			count_font = game.font.SysFont('Cambria',25)
 			ship_count = count_font.render(f'{available_ships[j]} x ', False, (0, 0, 0))
 			coord_x, coord_y = coords_unplaced_ships[j]
 			screen.blit(ship_count,(coord_x - sq_size, coord_y+0.1*sq_size))

def mouse_on_square(mouse_x, mouse_y):
	''' Detect on which square of the board the mouse is

	Input: mouse_x position, mouse_y position

	Output: 2-list with the corresponding row and column
	'''
	square_x = mouse_x // sq_size
	square_y = mouse_y // sq_size
	coord = [square_y, square_x]
	return coord

if __name__ == "__main__":
	ship_placing('name')