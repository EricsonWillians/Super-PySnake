#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  run.py
#  
#  Copyright 2015 Ericson Willians (Rederick Deathwill) <EricsonWRP@ERICSONWRP-PC>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import json
import pyglet
import os.path
from random import randint

NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3 

class Serializable:

	def __init__(self):
		self.file = None
		
	def serialize(self, path, mode):	
		try:
			self.file = open(path, mode)
		except:
			raise FileNotFoundError()
		if self.file is not None:
			return self.file
			self.file.close()

class App(Serializable, pyglet.window.Window):

	def __init__(self):
		Serializable.__init__(self)
		if os.path.isfile("config.txt"):
			self.data = self.load("config.txt")
		else:
			self.data = {
					"SCREEN_WIDTH": 1024,
					"SCREEN_HEIGHT": 768,
					"SQUARE_SIZE": 32,
					"GAME_SPEED": 0.1,
					"FULLSCREEN": True,
					"LOCKED_MOUSE": True,
					"DEFAULT_MAP_FILE": "default_map.txt",
					"TEXTURES": {"BACKGROUND": "GFX//background.png", "SNAKE": "GFX//snake.png", "FOOD": "GFX//food.png", "BRICK": "GFX//brick.png"}}
		self.write("config.txt")
		pyglet.window.Window.__init__(self, self.data["SCREEN_WIDTH"], self.data["SCREEN_HEIGHT"], fullscreen=self.data["FULLSCREEN"])
		if self.data["LOCKED_MOUSE"]:
			self.set_exclusive_mouse()

	def write(self, path):
		self.serialize(path, "w").write(json.dumps(self.data))
		
	def load(self, path):
		json_data = open(path, "r")
		self.data = json.load(json_data)
		json_data.close()
		return self.data

app = App()

class TSquare:
	
	def __init__(self, x, y, width, height, image):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.angle = 0
		self.size = 1
		self.image = image
		x = width/2.0
		y = height/2.0
		self.vlist = pyglet.graphics.vertex_list(4, ('v2f', [-x, -y, x, -y, -x, y, x, y]), ('t2f', [0, 0, 1, 0, 0, 1, 1, 1]))
		
	def draw(self):
		pyglet.gl.glPushMatrix()
		pyglet.gl.glTranslatef(self.x + self.width/2, app.data["SCREEN_HEIGHT"] + self.y - self.height/2, 0)
		pyglet.gl.glRotatef(self.angle, 0, 0, 1)
		pyglet.gl.glScalef(self.size, self.size, self.size)
		pyglet.gl.glColor3f(1,1,1)
		pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
		pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
		pyglet.gl.glEnable(pyglet.gl.GL_TEXTURE_2D)
		pyglet.gl.glBindTexture(pyglet.gl.GL_TEXTURE_2D, self.image.get_texture().id)
		pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D, pyglet.gl.GL_TEXTURE_MAG_FILTER, pyglet.gl.GL_LINEAR)
		pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D, pyglet.gl.GL_TEXTURE_MIN_FILTER, pyglet.gl.GL_LINEAR)
		self.vlist.draw(pyglet.gl.GL_TRIANGLE_STRIP)
		pyglet.gl.glDisable(pyglet.gl.GL_TEXTURE_2D)
		pyglet.gl.glPopMatrix()
		
class Dungeon:
	
	positions = [[(row, -column) for row in range(0, app.data["SCREEN_WIDTH"], 
					app.data["SQUARE_SIZE"])] for column in range(0, app.data["SCREEN_HEIGHT"], app.data["SQUARE_SIZE"])]
	
	def __init__(self, dungeon_map=[]):
		print(len(self.positions))
		print(self.positions)
		self.dungeon_map = dungeon_map
		brick_image = pyglet.image.load(app.data["TEXTURES"]["BRICK"])
		try:
			self.bricks = [(lambda: TSquare(self.positions[i][j][0], 
										self.positions[i][j][1], app.data["SQUARE_SIZE"], app.data["SQUARE_SIZE"], brick_image)
								if self.dungeon_map[i][j] == 1 else None)() 
								for i in range(len(self.positions)) 
									for j in range(len(self.positions[i]))]
		except IndexError:
			raise RuntimeError("You must provide a map of the size of the resolution.")
		
	def draw(self):
		[brick.draw() for brick in self.bricks if brick is not None]

class Food(TSquare):
	
	def __init__(self, dungeon_map=[]):
		self.pos = [(lambda: (Dungeon.positions[i][j], Dungeon.positions[i][j]) if dungeon_map[i][j] == 0 else None)() 
				for i in range(len(Dungeon.positions)) 
					for j in range(len(Dungeon.positions[i]))]
		self.pos = [pos for pos in self.pos if pos is not None]
		TSquare.__init__(self, self.get_random_pos()[0], 
							self.get_random_pos()[1], app.data["SQUARE_SIZE"], 
								app.data["SQUARE_SIZE"], pyglet.image.load(app.data["TEXTURES"]["FOOD"]))

	def reset_pos(self):
		random_pos = self.pos[randint(0, len(self.pos))][0]
		self.x = random_pos[0]
		self.y = random_pos[1]

	def get_random_pos(self):
		random_pos = self.pos[randint(0, len(self.pos))][0]
		return random_pos

class Snake:
	
	def __init__(self):
		self.direction = NORTH
		self.speed = app.data["GAME_SPEED"]
		self.default_body()
	
	def default_body(self):
		self.body = [TSquare(Dungeon.positions[11][15][0], 
						Dungeon.positions[11][15][1], 
							app.data["SQUARE_SIZE"], app.data["SQUARE_SIZE"], pyglet.image.load(app.data["TEXTURES"]["SNAKE"]))]
	
	def move(self, dt, food, dungeon_map):
		self.body.pop() if len(self.body) > 1 else None
		_next = self.body[0]
		def reset_all():
			self.default_body()
			food.reset_pos()
		[reset_all() for snake_piece in self.body[1:] if _next.x == snake_piece.x and _next.y == snake_piece.y]
		if self.direction == NORTH:
			_next = TSquare(_next.x, _next.y + app.data["SQUARE_SIZE"], 
								app.data["SQUARE_SIZE"], app.data["SQUARE_SIZE"], pyglet.image.load(app.data["TEXTURES"]["SNAKE"]))
			if self.body[0].x == food.x and self.body[0].y == food.y:
				self.body.append(_next)
				food.reset_pos()
		elif self.direction == SOUTH:
			_next = TSquare(_next.x, _next.y - app.data["SQUARE_SIZE"], app.data["SQUARE_SIZE"], 
								app.data["SQUARE_SIZE"], pyglet.image.load(app.data["TEXTURES"]["SNAKE"]))
			if self.body[0].x == food.x and self.body[0].y == food.y:
				self.body.append(_next)
				food.reset_pos()
		elif self.direction == WEST:
			_next = TSquare(_next.x - app.data["SQUARE_SIZE"], _next.y, app.data["SQUARE_SIZE"], 
								app.data["SQUARE_SIZE"], pyglet.image.load(app.data["TEXTURES"]["SNAKE"]))
			if self.body[0].x == food.x and self.body[0].y == food.y:
				self.body.append(_next)
				food.reset_pos()
		elif self.direction == EAST:
			_next = TSquare(_next.x + app.data["SQUARE_SIZE"], _next.y, app.data["SQUARE_SIZE"], 
								app.data["SQUARE_SIZE"], pyglet.image.load(app.data["TEXTURES"]["SNAKE"]))
			if self.body[0].x == food.x and self.body[0].y == food.y:
				self.body.append(_next)
				food.reset_pos()
		self.body.insert(0, _next)
		for i in range(len(Dungeon.positions)):
			for j in range(len(Dungeon.positions[i])):
				if dungeon_map[i][j] == 1:
					if _next.x == Dungeon.positions[i][j][0] and _next.y == Dungeon.positions[i][j][1]:
						reset_all()
		
		print([(snake_piece.x, snake_piece.y) for snake_piece in self.body])
				
	def draw(self):
		[snake_piece.draw() for snake_piece in self.body]

class SnakeMap(Serializable, Dungeon):
	
	def __init__(self):
		Serializable.__init__(self)
		self.default_map =	\
							\
		[
		[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
		]
		if os.path.isfile(app.data["DEFAULT_MAP_FILE"]):
			self.data = self.load(app.data["DEFAULT_MAP_FILE"])
		else:
			self.data = self.default_map
			self.write(app.data["DEFAULT_MAP_FILE"])
		Dungeon.__init__(self, self.data)

	def write(self, path):
		self.serialize(path, "w").write(json.dumps(self.data))
		
	def load(self, path):
		json_data = open(path, "r")
		self.data = json.load(json_data)
		json_data.close()
		return self.data

def main():

	bg = TSquare(0, 256, app.data["SCREEN_WIDTH"], 
					app.data["SCREEN_HEIGHT"]+app.data["SCREEN_HEIGHT"]/3, pyglet.image.load(app.data["TEXTURES"]["BACKGROUND"]))
	snake_map = SnakeMap()
	snake = Snake()
	food = Food(snake_map.data)

	@app.event
	def on_draw():
		app.clear()
		bg.draw()
		snake_map.draw()
		food.draw()
		snake.draw()
		
	snake.move(None, food, snake_map.data)
	
	@app.event
	def on_key_press(key, modifiers):
		if key == pyglet.window.key.UP or key == pyglet.window.key.W:
			snake.direction = NORTH
		elif key == pyglet.window.key.DOWN or key == pyglet.window.key.S:
			snake.direction = SOUTH
		elif key == pyglet.window.key.LEFT or key == pyglet.window.key.A:
			snake.direction = WEST
		elif key == pyglet.window.key.RIGHT or key == pyglet.window.key.D:
			snake.direction = EAST

	pyglet.clock.schedule_interval(snake.move, snake.speed, food, snake_map.data)
	pyglet.app.run()
	
	return 0

if __name__ == '__main__':
	
	main()
