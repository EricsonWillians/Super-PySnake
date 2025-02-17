"""
Manages the game's dungeon grid and wall rendering.
"""
from typing import List, Optional

import pyglet

from game.square import TexturedSquare
from game.types import (
    MapGrid,
    Position,
    PositionGrid,
    Size,
    TILE_EMPTY,
    TILE_WALL,
    MapSizeError
)
from game.app import window


class Dungeon:
    """Manages the game's grid system and wall rendering.
    
    The Dungeon class is responsible for:
    1. Creating and maintaining the game's position grid
    2. Loading and validating the game map
    3. Rendering the walls
    
    Attributes:
        positions: A 2D grid of all possible positions in the game
        map_data: The current map's wall configuration
        walls: List of wall objects to be rendered
    """
    
    def __init__(self, map_data: Optional[MapGrid] = None) -> None:
        """Initialize the dungeon with an optional map.
        
        Args:
            map_data: 2D grid of integers where 1 represents walls and 0 empty space.
                     If None, creates an empty grid.
                     
        Raises:
            MapSizeError: If the provided map doesn't match the grid dimensions
        """
        self.positions = self._create_position_grid()
        self.map_data = map_data if map_data is not None else []
        
        # Load wall texture
        self.wall_texture = pyglet.image.load(window.config["TEXTURES"]["BRICK"])
        
        # Create wall objects if map is provided
        if map_data:
            self._validate_map_size()
            self._create_walls()
    
    def _create_position_grid(self) -> PositionGrid:
        """Create a grid of all possible positions in the game."""
        rows = window.config["SCREEN_HEIGHT"] // window.config["SQUARE_SIZE"]
        cols = window.config["SCREEN_WIDTH"] // window.config["SQUARE_SIZE"]

        return [
            [
                Position(
                    x=col * window.config["SQUARE_SIZE"],
                    y=(rows - row - 1) * window.config["SQUARE_SIZE"]  # Flip vertically
                )
                for col in range(cols)
            ]
            for row in range(rows)
        ]
    
    def _validate_map_size(self) -> None:
        """Validate that the map dimensions match the position grid.
        
        Raises:
            MapSizeError: If dimensions don't match
        """
        if not self.map_data:
            return
            
        expected_rows = len(self.positions)
        expected_cols = len(self.positions[0]) if self.positions else 0
        
        actual_rows = len(self.map_data)
        actual_cols = len(self.map_data[0]) if self.map_data else 0
        
        if actual_rows != expected_rows or actual_cols != expected_cols:
            raise MapSizeError(
                f"Map size ({actual_rows}x{actual_cols}) doesn't match "
                f"grid size ({expected_rows}x{expected_cols})"
            )
    
    def _create_walls(self) -> None:
        """Create wall objects based on the map data."""
        self.walls: List[TexturedSquare] = []
        
        for i, row in enumerate(self.map_data):
            for j, tile in enumerate(row):
                if tile == TILE_WALL:
                    position = self.positions[i][j]
                    self.walls.append(
                        TexturedSquare(
                            position=position,
                            size=Size(
                                width=window.config["SQUARE_SIZE"],
                                height=window.config["SQUARE_SIZE"]
                            ),
                            texture_path=window.config["TEXTURES"]["BRICK"],
                            window=window
                        )
                    )
    
    def is_wall(self, position: Position) -> bool:
        """Check if a position contains a wall.
        
        Args:
            position: The position to check
            
        Returns:
            True if the position contains a wall, False otherwise
        """
        for wall in self.walls:
            if wall.position == position:
                return True
        return False
    
    def get_valid_positions(self) -> List[Position]:
        """Get all positions that don't contain walls.
        
        Returns:
            List of positions that are safe for other game objects
        """
        valid_positions = []
        for i, row in enumerate(self.map_data):
            for j, tile in enumerate(row):
                if tile == TILE_EMPTY:
                    valid_positions.append(self.positions[i][j])
        return valid_positions
    
    def draw(self) -> None:
        """Draw all walls in the dungeon."""
        for wall in self.walls:
            wall.draw()