"""
Core snake entity and movement logic.
"""

from typing import List

import pyglet

from game.app import window
from game.dungeon import Dungeon
from game.food import Food
from game.square import TexturedSquare
from game.types import (
    Direction,
    Position,
    Size,
    DEFAULT_SNAKE_POSITION,
)
from pyscored.adapters.game_frameworks import GameFrameworkAdapter

class Snake:
    """The player-controlled snake entity.

    Handles the snake's movement, growth, and collision detection.
    The snake is composed of multiple TexturedSquare segments.

    Attributes:
        direction: Current movement direction.
        speed: Movement speed (seconds per move).
        body: List of snake segments, with the head at index 0.
        dungeon: Reference to the game dungeon for collision detection.
    """

    def __init__(self, dungeon: Dungeon, game_adapter: GameFrameworkAdapter) -> None:
        """Initialize the snake with a single segment.

        Args:
            dungeon: The game dungeon for wall collision detection.
        """
        self.direction = Direction.NORTH
        self.speed = window.config["GAME_SPEED"]
        self.dungeon = dungeon
        self.game_adapter = game_adapter

        # Create the initial body segment (the head).
        self._create_default_body()

    def _create_default_body(self) -> None:
        """Reset the snake to its default state with a single segment."""
        start_pos = Position(
            x=window.config["SCREEN_WIDTH"] // 2,
            y=window.config["SCREEN_HEIGHT"] // 2
        )

        self.body = [
            TexturedSquare(
                position=start_pos,
                size=Size(
                    width=window.config["SQUARE_SIZE"],
                    height=window.config["SQUARE_SIZE"]
                ),
                texture_path=window.config["TEXTURES"]["SNAKE"],
                window=window
            )
        ]

    def _get_next_position(self) -> Position:
        """Calculate the next head position based on the current direction.

        Returns:
            The next grid position for the snake's head.
        """
        head = self.body[0]
        square_size = window.config["SQUARE_SIZE"]

        if self.direction == Direction.NORTH:
            return Position(head.position.x, head.position.y + square_size)
        elif self.direction == Direction.SOUTH:
            return Position(head.position.x, head.position.y - square_size)
        elif self.direction == Direction.WEST:
            return Position(head.position.x - square_size, head.position.y)
        else:  # Direction.EAST
            return Position(head.position.x + square_size, head.position.y)

    def _check_self_collision(self, position: Position) -> bool:
        """Check if a position collides with any snake segment (excluding the head).

        Args:
            position: The position to check for collision.

        Returns:
            True if a collision with the snake's body is detected.
        """
        return any(
            segment.position == position
            for segment in self.body[1:]
        )

    def _check_wall_collision(self, position: Position) -> bool:
        """Check if a position collides with a wall.

        Args:
            position: The position to check for collision.

        Returns:
            True if a wall collision is detected.
        """
        return self.dungeon.is_wall(position)

    def reset(self, food: Food) -> None:
        """Reset the snake to its initial state.

        Also resets the food's position.

        Args:
            food: The food object to reset.
        """
        self._create_default_body()
        food.reset_position([segment.position for segment in self.body])
        self.game_adapter.update_player_score("player1", points=-self.current_score)

    def move(self, dt: float, food: Food) -> None:
        """Update the snake's position and handle collisions.

        This method:
        1. Calculates the next head position.
        2. Checks for collisions with self or walls.
        3. Inserts a new head segment.
        4. Checks for food consumption and, if eaten, resets the food position
            (without removing the tail so the snake grows); otherwise, it removes the tail.
        
        Args:
            dt: Time delta from the Pyglet clock.
            food: The food object for collision checking.
        """
        # Determine the next position for the snake's head.
        next_pos = self._get_next_position()

        # Check collisions with self or walls.
        if self._check_self_collision(next_pos) or self._check_wall_collision(next_pos):
            self.reset(food)
            return
        
        # Check if the food is about to be eaten
        food_eaten = food.is_eaten(next_pos)

        # Create and insert the new head segment.
        new_head = TexturedSquare(
            position=next_pos,
            size=Size(
                width=window.config["SQUARE_SIZE"],
                height=window.config["SQUARE_SIZE"]
            ),
            texture_path=window.config["TEXTURES"]["SNAKE"],
            window=window
        )
        self.body.insert(0, new_head)

        if food_eaten:
            # Update player score through adapter
            self.game_adapter.update_player_score("player1", points=10)
            self.current_score = self.game_adapter.get_player_score("player1")
            print(f"Current score: {self.current_score}")
            food.reset_position([segment.position for segment in self.body])
        else:
            self.body.pop()


    def draw(self) -> None:
        """Draw all snake segments."""
        for segment in self.body:
            segment.draw()
