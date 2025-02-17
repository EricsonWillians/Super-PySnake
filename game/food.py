import random
from typing import List

import pyglet

from game.app import window
from game.dungeon import Dungeon
from game.square import TexturedSquare
from game.types import Position, Size, TILE_EMPTY

class Food(TexturedSquare):
    """Represents the food that the snake can eat.
    
    Attributes:
        dungeon: The game's dungeon instance for position validation.
        valid_positions: List of positions where the food can appear (no walls).
    """

    def __init__(self, dungeon: Dungeon) -> None:
        """Initialize the food object with a valid starting position."""
        self.dungeon = dungeon
        
        # Determine valid positions: Only tiles marked as TILE_EMPTY
        self.valid_positions = [
            dungeon.positions[i][j]
            for i, row in enumerate(dungeon.map_data)
            for j, tile in enumerate(row)
            if tile == TILE_EMPTY
        ]
        
        if not self.valid_positions:
            raise RuntimeError("No valid positions available for food placement.")
        
        # Set initial position
        initial_pos = self._get_random_position()
        
        super().__init__(
            position=initial_pos,
            size=Size(
                width=window.config["SQUARE_SIZE"],
                height=window.config["SQUARE_SIZE"]
            ),
            texture_path=window.config["TEXTURES"]["FOOD"],
            window=window
        )

    def _get_random_position(self) -> Position:
        """Get a random valid position for the food."""
        return random.choice(self.valid_positions)

    def reset_position(self, occupied_positions: List[Position]) -> None:
        """Move the food to a new random position, excluding occupied tiles.
        
        This method also updates the underlying sprite's position.
        """
        available_positions = [
            pos for pos in self.valid_positions 
            if pos not in occupied_positions
        ]
        
        if not available_positions:
            raise RuntimeError("No available positions for food placement.")
        
        new_position = random.choice(available_positions)
        self.position = new_position
        
        # Update the sprite's position by directly setting x and y.
        if hasattr(self, "sprite"):
            self.sprite.x = new_position.x
            self.sprite.y = new_position.y

    def is_eaten(self, head_position: Position) -> bool:
        """Check if the snake's head is at the food's position."""
        return self.position == head_position
