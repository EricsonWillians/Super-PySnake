# game/square.py

import pyglet
from pyglet.sprite import Sprite
from pyglet.graphics import Batch
from game.types import Position, Size


class TexturedSquare:
    """A textured square object that can be rendered in the game."""

    def __init__(
        self,
        position: Position,
        size: Size,
        texture_path: str,
        window: pyglet.window.Window,  # Add window parameter
    ) -> None:
        """Initialize a new textured square."""
        self.position = position
        self.size = size
        self.window = window  # Store the window
        self.batch = Batch()

        # Load texture and create a sprite
        image = pyglet.image.load(texture_path)
        self.sprite = Sprite(image, x=position.x, y=position.y, batch=self.batch)
        self.sprite.scale_x = size.width / image.width
        self.sprite.scale_y = size.height / image.height

    def draw(self) -> None:
        """Draw the textured square on the screen."""
        self.batch.draw()
