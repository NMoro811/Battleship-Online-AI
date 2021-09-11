'''
Contains the TextBox class
'''
import os
import pygame as game

game.init()
game.event.set_allowed([game.MOUSEBUTTONDOWN, game.KEYDOWN])
# TextBox design
inactive_color = game.Color("dark gray")
active_color = game.Color("black")
background_color = (0, 85, 128)
default_font = game.font.SysFont('Cambria',30)
# Buttons
green_tick = game.image.load(os.path.join("img", "check.png"))
green_tick = game.transform.scale(green_tick, (30, 30))
red_cross = game.image.load(os.path.join("img", "remove.png"))
red_cross = game.transform.scale(red_cross, (30, 30))

class TextBox():
	''' Creates simple input boxes for the user to introduce his/her username

	Attributes:
		pos_x				Horizontal position of the input box's rect (i.e., where the text is rendered)
		pos_y				Vertical position
		width				Textbox's width
		height				Textbox's width
		rect 				Creates a rectangle with the same dimensions
		background_rect		The rectangle containing the textbox and the two buttons
		original_text		Default text to be displayed if the textbox is empty
		text 				Introduced by the user as their name
		font 				Text's font
		active 				Checks if the textbox has been clicked on
		color 				Current color of the textbox's borders
		text_surf			To display the introduced text
		finished			0 if text is still being introduced, 1 if done
		final_str			Entered string

	Methods:
		handle_event		Modifies the textbox for a given PyGame event
		draw				Draw the TextBox, the rectangle that contains it, and display the buttons
	'''
	def __init__(self, pos_x, pos_y, width, height, player_num):
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.width = width
		self.height = height
		self.rect = game.Rect(pos_x, pos_y, width, height)
		self.background_rect = self.rect.inflate(pos_x*0.5, pos_y*0.5)
		if player_num == 0:
			self.original_text = "Username" # To be used in Player vs CPU or LAN/Online
		elif player_num == 1:
			self.original_text = "Player1" # Player 1 in Local gameplay
		else:
			self.original_text = "Player2" # Player 2 in Local gameplay
		self.text = self.original_text
		self.font = default_font
		self.active = False # Inactive textbox by default
		self.color = inactive_color # Default colour is inactive
		self.text_surf = default_font.render(self.text, True, self.color)
		self.finished = 0
		self.final_str = self.text

	def handle_event(self, event):
		''' Handle the given PyGame event

		Input: (PyGame) event

		Output: None
		'''
		# Set up the two buttons' coordinates and store their rect surfaces
		bottom_right = self.background_rect.bottomright
		green_tick_coords = (bottom_right[0]-80, bottom_right[1]-50)
		green_tick_rect = green_tick.get_rect(topleft=green_tick_coords)
		red_cross_coords = (bottom_right[0]-40, bottom_right[1]-50)
		red_cross_rect = red_cross.get_rect(topleft=red_cross_coords)

		# Used to activate the TextBox, give it the corresponding color, and swap the
		# default text with an empty string (and vice versa)
		if event.type == game.MOUSEBUTTONDOWN:
			mouse_pos = event.pos
			# Clicked on the text box
			if self.rect.collidepoint(mouse_pos):
				self.active = not self.active
			# Clicked on the green 'Enter' button
			elif green_tick_rect.collidepoint(mouse_pos):
				self.active = False
				self.finished = 1
				self.final_str = self.text
				return
			# Clicked on the red 'Discard' button
			elif red_cross_rect.collidepoint(mouse_pos):
				self.active = False
				self.finished = 1
				return "red_cross"
			# Clicked elsewhere
			else:
				self.active = False

			# Modify input box's color and text
			if self.active:
				self.color = active_color
				if self.text == self.original_text:
					self.text = ''
			else:
				self.color = inactive_color
				if self.text == '':
					self.text = self.original_text
		# Used for typing the username down
		elif event.type == game.KEYDOWN:
			if self.active:
				# Pressed 'Enter' key
				if event.key == game.K_RETURN:
					self.finished = 1
					self.final_str = self.text
					return
				# Pressed 'Backspace' key
				elif event.key == game.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					self.text += event.unicode
		# Add a (non-blinking) bar '|' if the text box is active
		if self.active:
			self.text_surf = default_font.render(self.text+'|', True, self.color)
		else:
			self.text_surf = default_font.render(self.text, True, self.color)

	def draw(self, screen):
		# Set up the two buttons' coordinates and store their rect surfaces
		bottom_right = self.background_rect.bottomright
		green_tick_coords = (bottom_right[0]-80, bottom_right[1]-50)
		green_tick_rect = green_tick.get_rect(topleft=green_tick_coords)
		red_cross_coords = (bottom_right[0]-40, bottom_right[1]-50)
		red_cross_rect = red_cross.get_rect(topleft=red_cross_coords)

		# Draw all components
		game.draw.rect(screen, background_color, self.background_rect)
		screen.blit(green_tick, green_tick_coords)
		screen.blit(red_cross, red_cross_coords)
		game.draw.rect(screen, (255,255,255), self.rect)
		screen.blit(self.text_surf, (self.rect.x+5, self.rect.y+5))
		game.draw.rect(screen, self.color, self.rect, 2)