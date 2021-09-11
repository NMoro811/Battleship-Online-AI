'''
Module containing the main gameplay; given any two players (human or CPU), they will try to
guess each other's fleet's locations until all 10 ships have been sunk. The player who sinks
the other player's ships first wins (there is no draw).
'''

# EXTERNAL MODULES
import os
import pygame as game
from random import randint, shuffle, sample
from time import sleep

# INTERNAL MODULES
from board_class import Ship, BoardState
from cpu_class import CPU
from player_class import Player
from player_places_ships import *

game.init()
game_font = game.font.SysFont('Cambria',20)
square_font = game.font.SysFont('Cambria',14)
screen = game.display.set_mode((width, height))
colors = [(0, 105, 148), game.Color("cyan"), game.Color("black")]
game.event.set_allowed([game.QUIT, game.MOUSEBUTTONDOWN])

def battleship(users):
	''' Main gameplay function

	Input: list of users

	Output: print who has won (return = None)
	'''

	global square_list
	game_on = True

	# Initialize each player depending on its type
	for user_num in range(2):
		# If list entry is CPU()
		if isinstance(users[user_num], CPU):
			cpu = users[user_num]
			cpu.board = BoardState()
			# Place ships
			cpu.place_ships()
			# Create and store list of available squares to shoot at
			init_available_squares(cpu, square_list)
		# List entry is like 'username'
		else:
			name = users[user_num]
			# Create Player instance and execute player_places_ships' main function until player has
			# placed all ships on the board and pressed 'Ready'
			users[user_num] = ship_placing(name)
			# Reassign 'user' name
			user = users[user_num]
			# If player quits while placing ships, close the program
			if not user.placing_ships and len(user.board.placed_ships) < 10:
				game_on = False
				return

	# Shuffle user list so that who goes first is random
	shuffle(users)
	user_1 = users[0] # Goes first
	user_2 = users[1] # Goes second
	next_player_turn = False

	# Store all the 100 squares on the board if it has not been done yet
	if len(square_list) == 0:
		square_list = collect_squares(square_list)

	# Main game loop
	while game_on:

		# Check if the opponent won in the previous round; if so, finish the game
		if len(user_1.board.sunk_ships) == 10:
			game_on = False
			user_lost = user_1
			user_won = user_2
			sleep(2)
			screen.fill((0, 0, 0))
			game.display.update()
			break

		# Player's turn
		if isinstance(user_1, Player):
			screen.blit(background, (0, 0))

			mouse_x, mouse_y = game.mouse.get_pos()
				
			for e in game.event.get():
				if e.type == game.QUIT:
					game_on = False
				if e.type == game.MOUSEBUTTONDOWN:
					row = mouse_on_square(mouse_x, mouse_y)[0]
					col = mouse_on_square(mouse_x, mouse_y)[1]
					# If pressed on a square on the board, handle the player's guess and check if
					# it is the next player's turn
					if row < 10 and col < 10:
						next_player_turn = shot_outcome(user_1, user_2, row, col)

			draw_board(user_1, screen, colors, square_list, letter_dict, number_dict, square_font)

			mouse_x, mouse_y = game.mouse.get_pos()
			row = mouse_on_square(mouse_x, mouse_y)[0]
			col = mouse_on_square(mouse_x, mouse_y)[1]
			# Highlight square if it hasn't been shot at yet
			if row < 10 and col < 10:
				highlight_square(user_1, screen, colors, mouse_x, mouse_y, letter_dict, number_dict, square_font)
			# Show number of tries and who's turn it is
			show_tries(user_1, users, screen, game_font, (520,100))
			show_player(user_1, users, screen, game_font, (520,300))

			game.display.update()

			# Move on to the next player
			if next_player_turn:
				sleep(0.5)
				user_1, user_2 = swap_users(user_1, user_2)
				next_player_turn = False

		# CPU logic tries to guess the player's ships' locations in a random fashion (difficulty: 'normal')
		elif isinstance(user_1, CPU):
			screen.blit(background, (0, 0))
			draw_board(user_1, screen, colors, square_list, letter_dict, number_dict, square_font)
			show_tries(user_1, users, screen, game_font, (520,100))
			show_player(user_1, users, screen, game_font, (520,300))
			game.display.update()

			# If CPU is not scanning for a ship yet (after hitting it for the first time), shoot
			# at a square on the board in a random fashion
			if type(user_1.currently_hit_ship) != str:
				ship = user_1.currently_hit_ship
				# If only hit one block of the ship, scan around it until a second block is hit
				if len(ship.hit_blocks) == 1:
					row, col = user_1.current_scanned_coord
					# If a block has been hit in the previous turn
					if user_1.board.guess_state[row][col] == 'X':
						potential_locations = []
						# Fill potential_locations with all the squares where the next block might be
						for i in range(-1,2):
							for j in range(-1,2):
								if i != j and 0 in {i,j}:
									new_row = row + i
									new_col = col + j
									if new_row in range(10) and new_col in range(10):
										if (new_row, new_col) in user_1.available_squares:
											potential_locations.append((new_row, new_col))
						# Pick one of the potential locations at random and try shooting at it
						shuffle(potential_locations)
						row, col = potential_locations.pop(0)
					# If the last potential location was a miss, pick the next one until the search concludes
					else:
						row, col = potential_locations.pop(0)

				# If more than one block of this ship has been hit, continue shooting along the same direction
				# until the ship has been sunk or the CPU misses, in which cases the direction is reversed along
				# the same axis.
				elif len(ship.hit_blocks) > 1:
					# At this point, the CPU has already 'found out' whether the ship is placed vertically or horizontally
					# Note that 'user_1.current_scanned_coord' has been updated in 'shot_outcome'
					row, col = user_1.current_scanned_coord
					hit_block_0 = ship.hit_blocks[0] # First block of the ship that was hit
					hit_block_1 = ship.hit_blocks[-1] # Last block of the ship that was hit
					if ship.vertical:
						# Direction: +1 is down, -1 is up
						direction = int((hit_block_1[0] - hit_block_0[0])/abs(hit_block_1[0] - hit_block_0[0]))
						if user_1.board.guess_state[row][col] == 'M' or (row+direction, col) not in user_1.available_squares:
							# Go back to the first hit_block and reverse the direction
							row = hit_block_0[0]-direction
						else:
							# Go along the same direction
							row += direction
					else:
						# Direction: +1 is right, -1 is left
						direction = int((hit_block_1[1] - hit_block_0[1])/abs(hit_block_1[1] - hit_block_0[1]))
						if user_1.board.guess_state[row][col] == 'M' or (row, col+direction) not in user_1.available_squares:
							# Go back to the first hit_block and reverse the direction
							col = hit_block_0[1]-direction
						else:
							# Go along the same direction
							col += direction
				# The square we're shooting at needs to be removed from the available choices
				user_1.available_squares.remove((row,col))

			# If not scanning for a ship, shoot at a random set of coordinates out of the available ones
			else:
				available_num = len(user_1.available_squares)
				indx = randint(0,available_num-1)
				row, col = user_1.available_squares[indx]
				user_1.available_squares.pop(indx)

			# Handle CPU guess and move on to the next player
			next_player_turn = shot_outcome(user_1, user_2, row, col)

			# Update display
			sleep(0.5)
			draw_board(user_1, screen, colors, square_list, letter_dict, number_dict, square_font)
			show_tries(user_1, users, screen, game_font, (520,100))
			show_player(user_1, users, screen, game_font, (520,300))
			game.display.update()

			if next_player_turn:
				sleep(1)
				user_1, user_2 = swap_users(user_1, user_2)
				next_player_turn = False

	# Print who has won
	# Will make it visual in future updates
	if len(user_1.board.sunk_ships) == 10:
		if isinstance(user_won, Player):
			print(f"{user_won.name} has won! Congratulations!")
		else:
			print("The CPU has won! Better luck next time.")
		#input("Press Enter to exit the program. ")

# FUNCTIONS

def swap_users(user_1, user_2):
	''' Swap one user for another when it's the other player's turn; might modify/exclude in future versions

	Input: user_1, user_2

	Output: (user_2, user_1)
	'''
	temp_user = user_2
	user_2 = user_1
	user_1 = temp_user
	return (user_1, user_2)

def shot_outcome(user, opponent, row, col):
	''' Handle the user's guess

	Input: user, opponent, row, col
	Output: next_player_turn boolean
	'''
	# Only check if the given square has not been fired upon yet
	if user.board.guess_state[row][col] not in {'S', 'X', 'M'}:

		# Case 1: 'Hit'
		if opponent.board.state[row][col] == 'X':
			user.num_of_tries += 1
			# Find out which of the rival's ships has been hit by looping through the indices
			findr_indx = 0
			while findr_indx in range(len(opponent.board.placed_ships)):
				ship = opponent.board.placed_ships[findr_indx]
				if (row,col) in ship.locations:
					ship.hit_blocks.append((row,col))
					break
				else:
					findr_indx += 1
			# Check if the rival's ship has been sunk; if so, update the color of all hit blocks
			if ship.check_if_sunk():
				opponent.board.sunk_ships.append(ship)
				# Change all the 'X' of the hit ship to 'S' in the relevant boards
				for sunk_coords in ship.hit_blocks:
					(sunk_x, sunk_y) = sunk_coords
					opponent.board.state[sunk_x][sunk_y] = 'S'
					user.board.guess_state[sunk_x][sunk_y] = 'S'
					# If the CPU is playing: store the sunk ship & its surroundings
					if isinstance(user,CPU):
						sunk_block_surroundings = user.board.get_surroundings(sunk_x, sunk_y)
						user.discarded_blocks = user.discarded_blocks.union(sunk_block_surroundings)
				# For the CPU: discard the sunk ship & its surroundings from the list of
				# available squares. Update the currently_hit_ship and current_scanned_coord
				# attributes to stop scanning for the hit ship.
				if isinstance(user,CPU):
					user.available_squares = list(filter(lambda item: item not in user.discarded_blocks, user.available_squares))
					user.currently_hit_ship = ''
					user.current_scanned_coord = ()
				# Opponent plays next
				next_player_turn = True
				return next_player_turn
			else:
				# Hit but not sunk
				opponent.board.state[row][col] = 'H'
				user.board.guess_state[row][col] = 'X'
				if isinstance(user,CPU):
					user.currently_hit_ship = ship
					user.current_scanned_coord = (row, col)
				next_player_turn = True
				return next_player_turn

		# Case 2: 'Miss'
		elif opponent.board.state[row][col] in {'O',' '}:
			user.num_of_tries += 1
			user.board.guess_state[row][col] = 'M'
			if isinstance(user,CPU):
				user.current_scanned_coord = (row, col)
			next_player_turn = True
			return next_player_turn
	else:
		pass # Do nothing if square has already been fired upon

def draw_board(user, screen, colors, square_list, letter_dict, number_dict, square_font):
	''' Display the board. 
		Note: this function is different from that in the player_places_ships module.

	Input: user, screen, colors, square_list, letter_dict, number_dict, square_font
	
	Output: None
	'''
	for square in square_list:
		c = square.left // sq_size
		r = square.top // sq_size
		# Paint the sunk squares black
		if user.board.guess_state[r][c] == 'S':
			game.draw.rect(screen, game.Color("black"), square)
			text_color = (255,255,255)
		# Paint the hit squares green
		elif user.board.guess_state[r][c] == 'X':
			game.draw.rect(screen, game.Color("green"), square)
			text_color = (255,255,255)
		# For the CPU: paint ship surroundings in a light blue-ish color
		elif (r,c) in user.discarded_blocks:
			game.draw.rect(screen, (59, 174, 254), square)
			text_color = (59, 174, 254) # Invisible
		# Misses are red
		elif user.board.guess_state[r][c] == 'M':
			game.draw.rect(screen, game.Color("red"), square)
			text_color = (255,255,255)
		# The rest of the squares are displayed as usual
		else:
			color = colors[((r+c)%2)]
			text_color = colors[((r+c-1)%2)]
			game.draw.rect(screen, color, square)
		
		# Display letter/number in first row/column
		row_letter = letter_dict[r]
		col_number = number_dict[c]

		row_text = square_font.render(f'{row_letter}', False, text_color)
		if c == 0:
			screen.blit(row_text, (square.topleft[0]+2, square.topleft[1]))

		col_text = square_font.render(f'{col_number}', False, text_color)
		if r== 0:
			screen.blit(col_text, (square.bottomright[0]-15, square.bottomright[1]-17.5))

def highlight_square(user, screen, colors, mouse_x, mouse_y, letter_dict, number_dict, square_font):
	''' Higlight the square the mouse is on. Note: slightly different from the function in the
		player_places_ships module.
	'''
	# Create the square
	row = mouse_on_square(mouse_x, mouse_y)[0]
	col = mouse_on_square(mouse_x, mouse_y)[1]
	square = game.Rect(col*sq_size, row*sq_size, sq_size, sq_size)

	# Set up text on the square
	text_color = colors[((row+col-1)%2)]
	row_letter = letter_dict[row]
	col_number = number_dict[col]

	row_text = square_font.render(f'{row_letter}', False, text_color)
	col_text = square_font.render(f'{col_number}', False, text_color)

	# If the square has not been shot at (and, for the CPU, if also not included in any surroundings), do
	# highlight the square
	if user.board.guess_state[row][col] == " ": 
		# Draw squares
		color = colors[((row+col)%2)]
		game.draw.rect(screen, colors[2], square)
		if col < 9 and row < 9:
			game.draw.rect(screen, color, game.Rect(col*sq_size+2, row*sq_size+2, sq_size+2, sq_size+2))
		else:
			game.draw.rect(screen, color, game.Rect(col*sq_size+2, row*sq_size+2, sq_size, sq_size))
		# Coordinate letters
		if col == 0:
			screen.blit(row_text, (square.topleft[0]+4, square.topleft[1]+2))
		if row == 0:
			screen.blit(col_text, (square.bottomright[0]-13, square.bottomright[1]-15.5))
	else:
		pass

def init_available_squares(user, square_list):
	'''
	Initialize square_list
	'''
	for square in square_list:
		col, row = (square.left // sq_size, square.top // sq_size)
		user.available_squares.append((row,col))

def show_tries(user, users, screen, game_font, position):
	''' Display how many shots the user has fired.

	Input: user, users, screen, game_font, position

	Output: None
	'''
	score = game_font.render(f'Number of tries: {user.num_of_tries}', False, (255, 255, 255))
	(score_x, score_y) = position
	# Dark blue-ish for the first player, orange for the one who goes second
	if user == users[0]:
		color = (0, 105, 148)
	else:
		color = game.Color("orange")
	game.draw.rect(screen, color, game.Rect(score_x-5, score_y-5, sq_size*3.7, sq_size*0.75))
	screen.blit(score, position)

def show_player(user, users, screen, game_font, position):
	''' Show whose turn it is

	Input: user, users, screen, game_font, position

	Output: None
	'''
	if isinstance(user, CPU):
		name = "CPU"
	else:
		name = user.name
	# Render text
	player_name = game_font.render(f'Playing: {name}', False, (255, 255, 255))
	# Design the box that contains the text
	(name_x, name_y) = position
	color = game.Color("black")
	game.draw.rect(screen, color, game.Rect(name_x-5, name_y-5, sq_size*3.7, sq_size*0.75))
	screen.blit(player_name, position)

if __name__ == "__main__":
	#battleship(['name', 'name2']) # Player vs Player
	battleship(['name', CPU()])  # Player vs CPU (current difficulty level: 'normal')