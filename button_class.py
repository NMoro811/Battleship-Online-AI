'''
Contains the Button class
'''

import pygame as game

class Button():
	''' This class is used to automate the creation of buttons for the game.
		Note: mostly used in menu.py, but I plan to modify player_places_ships to 
		make use of it as well.

	Attributes:
		pressed		Checks if the button has been pressed
		mouse_on	Checks if the mouse is over the button to higlight it
		pos_x		Horizontal position of the button
		pos_y		Vertical position of the button
		width 		Button's width
		height 		Button's height
		rectangle	Creates a rectangle surface with the button's dimensions
		color 		Button's background color
		text_color	Color of the render text

	Methods:
		mouse_over	Updates the mouse_on attribute, given the mouse's position
		draw		Draws the button
	'''
	pressed = False
	mouse_on = False
	def __init__(self, pos_x, pos_y, width, height, color, text_color):
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.width = width
		self.height = height
		self.rectangle = game.Rect(self.pos_x,self.pos_y,self.width,self.height)
		# Accepts both strings (e.g., "red") and rgb ((255,0,0) in the same example)
		if type(color) == str:
			self.color = game.Color(color)
		else:
			self.color = color
		# Same as for the color attribute
		if type(text_color) == str:
			self.text_color = game.Color(text_color)
		else:
			self.text_color = text_color

	def mouse_over(self, mouse_pos):
		# Set mouse_on to True if, and only if, the mouse's position collides with the button's rect
		if self.rectangle.collidepoint(mouse_pos):
			self.mouse_on = True
		else:
			self.mouse_on = False
		return self.mouse_on

	def draw(self, screen, text, font):
		color_1 = self.color
		color_2 = self.text_color
		# Invert the colors if the button is being highlighted, i.e., if the mouse is over it
		if self.mouse_on:
			color_1, color_2 = color_2, color_1
		# Draw the button and render the text
		game.draw.rect(screen, color_1, self.rectangle)
		button_text = font.render(text, False, color_2)
		screen.blit(button_text, (self.pos_x + (self.width/2 - button_text.get_width()/2), self.pos_y + (self.height/2 - button_text.get_height()/2)))