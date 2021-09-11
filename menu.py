'''
Main module: executes the menu with the different gameplay options. Most of these are to be
incorporated in the future. Current version only includes the possibility to play locally, against
either the CPU ('normal' difficulty) or another player
'''

import os
from button_class import Button
from player_places_ships import *
from battleship import *
from textbox_class import TextBox

# TITLE AND GAME ICON (TEMPORARY!)
os.environ['SDL_VIDEO_CENTERED'] = "1" # Not working?
game.display.set_caption("Battleship Online")
icon = game.image.load(os.path.join("img", "ship.png"))
game.display.set_icon(icon)

# Menu display settings
game.init()
game.event.set_allowed([game.QUIT, game.MOUSEBUTTONDOWN])
background = game.image.load(os.path.join("img", "menu_pic2.jpg"))
background_2 = game.image.load(os.path.join("img", "menu_pic3.jpg"))
menu_width = 1072
menu_height = 712
menu_screen = game.display.set_mode((menu_width, menu_height))

def main():
	''' Main function of the module. Displays the different screens of the menu.
		The menu consists of different loops, each one of them corresponding to its own scren.

		Input: None

		Output: None
	'''
	# Start by displaying the main menu
	display_menus = True
	main_menu = True
	new_game = False
	top_scores = False
	options = False

	# Will store the players before executing battleship.py
	list_of_players = []
	# The four modalities of gameplay that will be available in the future
	# Currently, only the first two are present
	modalities = {1: "CPU", 2: "Local", 3: "LAN", 4: "Online"}

	# Creating and storing the buttons of the main menu
	button_list = []
	button_font = game.font.SysFont('Cambria',26)
	for i in range(4):
		new_button = Button(100+i*240, 600, sq_size*3, sq_size*0.75, (0, 85, 128), (255, 255, 255))
		button_list.append(new_button)

	# Will store the buttons of the other three screens
	new_game_buttons = []
	top_scores_buttons = []
	options_buttons = []

	# Create four buttons for the 'New Game' screen. All screens (except the main one) have a 'Return' button.
	return_button = Button(50, 50, sq_size*3, sq_size*0.75, (0, 85, 128), (255, 255, 255))
	new_game_buttons.append(return_button)
	for i in range(4):
		button_width = sq_size*8
		button_height = sq_size*0.75
		if i < 2: # Temporary! Will take out after incorporating LAN & Online modes
			new_button = Button((menu_width-button_width)/2, 125+i*150, button_width, button_height, (0, 85, 128), (255, 255, 255))
		else:
			new_button = Button((menu_width-button_width)/2, 125+i*150, button_width, button_height, game.Color("gray"), (255, 255, 255))
		new_game_buttons.append(new_button)
	top_scores_buttons.append(return_button)
	options_buttons.append(return_button)

	# Main loop
	while display_menus:

		# Corresponds to the main menu, where one can choose out of four options: 'New Game', 
		# 'Top Scores', 'Options', and 'Quit'. Currently, 'Top Scores' and 'Options' will only
		# display a 'Coming Soon' message
		while main_menu:

			menu_screen.blit(background, (0, 0))
			mouse_pos = game.mouse.get_pos()

			for e in game.event.get():
				if e.type == game.QUIT:
					main_menu = False
					display_menus = False
				elif e.type == game.MOUSEBUTTONDOWN:
					if e.button == 1:
						for button in button_list:
							if button.mouse_on:
								button.pressed = True
								break
				# Due to the event limitation, this means that the mouse has not been clicked anywhere
				else:
					for button in button_list:
						# Updates button's 'mouse_on' boolean
						button.mouse_over(mouse_pos)

			# Check which button has been pressed and activate the corresponding loop (or quit)
			text_dict = {0: "New Game", 1: "Top Scores", 2:"Options", 3: "Quit"}
			for i in range(len(text_dict)):
				button = button_list[i]
				button.draw(menu_screen, text_dict[i], button_font)
				if button.pressed:
					# 'New Game' selected
					if i == 0:
						new_game = True
						main_menu = False
					# 'Top Scores' selected
					elif i == 1:
						top_scores = True
						main_menu = False
					# 'Options' selected
					elif i == 2:
						options = True
						main_menu = False
					# 'Quit' selected
					else:
						main_menu = False
						display_menus = False
					button.pressed = False

			game.display.update()

		# Play a new game
		while new_game:

			menu_screen.blit(background_2, (0, 0))
			mouse_pos = game.mouse.get_pos()

			for e in game.event.get():
				if e.type == game.QUIT:
					new_game = False
					display_menus = False
				elif e.type == game.MOUSEBUTTONDOWN:
					if e.button == 1:
						for button in new_game_buttons:
							if button.mouse_on:
								button.pressed = True
								break
				# Due to the event limitation, this means that the mouse has not been clicked anywhere
				else:
					for button in new_game_buttons:
						# Updates button's 'mouse_on' boolean
						button.mouse_over(mouse_pos)

			# Check which modality has been chosen if a button has been pressed
			modality = " "
			text_dict = {0: "Return", 1: "Play vs CPU", 2:"Play vs A Friend (Local)", 3: "LAN Game - Unavailable", 4: "Play Online - Unavailable"}
			for i in range(len(text_dict)):
				button = new_game_buttons[i]
				button.draw(menu_screen, text_dict[i], button_font)
				if button.pressed:
					if i == 0:
						new_game = False
						main_menu = True
					else:
						modality = modalities[i]
					button.pressed = False

			game.display.update()

			# Play the chosen modality
			game_result = ''
			if modality == "CPU":
				game_result = play_vs_cpu(menu_screen)
			elif modality == "Local":
				game_result = play_local(menu_screen)
			elif modality == "LAN":
				game_result = play_lan()
			elif modality == "Online":
				game_result = play_online()

			# The user has quit during the game or while writing the usernames
			if game_result == None:
				new_game = False
				display_menus = False
			# Username discarded in the TextBox
			elif game_result == 404:
				continue

		# Display the game's top scores
		while top_scores:

			menu_screen.blit(background_2, (0, 0))
			mouse_pos = game.mouse.get_pos()

			for e in game.event.get():
				if e.type == game.QUIT:
					top_scores = False
					display_menus = False
				elif e.type == game.MOUSEBUTTONDOWN:
					if e.button == 1:
						for button in top_scores_buttons:
							if button.mouse_on:
								button.pressed = True
								break
				# Due to the event limitation, this means that the mouse has not been clicked anywhere
				else:
					for button in top_scores_buttons:
						# Updates button's 'mouse_on' boolean
						button.mouse_over(mouse_pos)

			# Only the return button is currently available
			text_dict = {0: "Return"}
			for i in range(len(text_dict)):
				button = top_scores_buttons[i]
				button.draw(menu_screen, text_dict[i], button_font)
				if button.pressed:
					if i == 0:
						top_scores = False
						main_menu = True
					button.pressed = False

			# 'Coming Soon' rectangle
			coming_soon()

			game.display.update()

		# Change music volume and other settings
		while options:

			menu_screen.blit(background_2, (0, 0))
			mouse_pos = game.mouse.get_pos()

			for e in game.event.get():
				if e.type == game.QUIT:
					options = False
					display_menus = False
				elif e.type == game.MOUSEBUTTONDOWN:
					if e.button == 1:
						for button in options_buttons:
							if button.mouse_on:
								button.pressed = True
								break
				# Due to the event limitation, this means that the mouse has not been clicked anywhere
				else:
					for button in options_buttons:
						# Updates button's 'mouse_on' boolean
						button.mouse_over(mouse_pos)

			# Only the return button is currently available
			text_dict = {0: "Return"}
			for i in range(len(text_dict)):
				button = options_buttons[i]
				button.draw(menu_screen, text_dict[i], button_font)
				if button.pressed:
					if i == 0:
						options = False
						main_menu = True
					button.pressed = False

			# 'Coming Soon' rectangle
			coming_soon()

			game.display.update()

def coming_soon():
	'''
		Display 'Coming Soon' message to indicate a future implementation.
	'''
	rec_width = 8*sq_size
	rec_height = 2*sq_size
	game.draw.rect(screen, game.Color("black"), game.Rect((menu_width - rec_width)/2, (menu_height - rec_height)/2, rec_width, rec_height))
	font = game.font.SysFont('Cambria',50)
	text = font.render("Coming Soon...", False, (255,255,255))
	menu_screen.blit(text, ((menu_width - rec_width)/2 + (rec_width/2 - text.get_width()/2), (menu_height - rec_height)/2 + (rec_height/2 - text.get_height()/2)))

def enter_username(screen, player_num, background = background_2):
	''' Text box to introduce username
	
	Input: screen, player_num, background

	Output: introduced username
	'''
	pos_x, pos_y, width, height = (350, 300, 350, 50)
	textbox = TextBox(pos_x, pos_y, width, height, player_num)

	# Display the input box and interact with it until a username has been entered or
	# the 'Discard' button has been pressed
	while not textbox.finished:
		screen.blit(background, (0, 0))

		for e in game.event.get():
			if e.type == game.QUIT:
				return
			else:
				handle_result = textbox.handle_event(e)
				if handle_result == "red_cross":
					return 404

		textbox.draw(menu_screen)
		game.display.update()
	return textbox.final_str

def play_vs_cpu(screen):
	''' 
		First modality: local game vs the CPU
	'''
	player_name = enter_username(screen, 0) # Player 0: plays alone
	if player_name == None:
		return
	elif player_name == 404: # might change for a different value later on
		return 404
	else:
		battleship([player_name, CPU()])

def play_local(screen):
	'''
		Second modality: local game vs a friend
	'''
	player1_name = enter_username(screen, 1) # Player 1
	if player1_name == None:
		return
	elif player1_name == 404:
		return 404
	else:
		player2_name = enter_username(screen, 2) # Player 2
		if player2_name == None:
			return
		elif player2_name == 404:
			return 404
		else:
			battleship([player1_name, player2_name])

def play_lan():
	'''
		Third modality: play a game in LAN (to be incorporated)
	'''
	print("Start a LAN game vs a friend...")
	pass

def play_online():
	'''
		Fourth modality: play an online game (to be incorporated)
	'''
	print("Play Online (need to set up a server)...")
	pass

if __name__ == "__main__":
	main()
