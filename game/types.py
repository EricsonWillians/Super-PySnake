"""
Core types and data structures for the Snake game.
"""
from enum import IntEnum
from pathlib import Path
from typing import Dict, List, NamedTuple, Protocol, TypeAlias, TypedDict, Union


class Direction(IntEnum):
    """Movement directions in the game, matching original constants."""
    NORTH = 0
    SOUTH = 1
    WEST = 2
    EAST = 3


class Position(NamedTuple):
    """A 2D position in the game grid."""
    x: float
    y: float


class Size(NamedTuple):
    """Dimensions for game objects."""
    width: float
    height: float


# Configuration Types
class TextureConfig(TypedDict):
    """Texture file paths configuration."""
    BACKGROUND: str
    SNAKE: str
    FOOD: str
    BRICK: str


class GameConfig(TypedDict):
    """Complete game configuration structure matching original config.txt."""
    SCREEN_WIDTH: int
    SCREEN_HEIGHT: int
    SQUARE_SIZE: int
    GAME_SPEED: float
    FULLSCREEN: bool
    LOCKED_MOUSE: bool
    DEFAULT_MAP_FILE: str
    TEXTURES: TextureConfig


# Map Types
class MapPosition(NamedTuple):
    """Position in the game map grid."""
    row: int
    column: int


# Type aliases for clarity
MapGrid: TypeAlias = List[List[int]]
PositionGrid: TypeAlias = List[List[Position]]
FilePath: TypeAlias = Union[str, Path]

# Game object types
class Drawable(Protocol):
    """Protocol for objects that can be drawn."""
    def draw(self) -> None: ...


class Moveable(Protocol):
    """Protocol for objects that can move."""
    direction: Direction
    speed: float


class Serializable(Protocol):
    """Protocol for objects that can be serialized."""
    def serialize(self, path: FilePath, mode: str) -> None: ...
    def write(self, path: FilePath) -> None: ...
    def load(self, path: FilePath) -> None: ...


# Game State Types
class CollisionObject(NamedTuple):
    """Represents an object that can be collided with."""
    position: Position
    size: Size


class SnakeSegment(NamedTuple):
    """Individual segment of the snake's body."""
    position: Position
    size: Size


# Constants
TILE_EMPTY = 0
TILE_WALL = 1

# Default starting position (from original code)
DEFAULT_SNAKE_POSITION = MapPosition(row=11, column=15)

# Window configuration defaults (matching original)
DEFAULT_CONFIG: GameConfig = {
    "SCREEN_WIDTH": 1024,
    "SCREEN_HEIGHT": 768,
    "SQUARE_SIZE": 32,
    "GAME_SPEED": 0.1,
    "FULLSCREEN": False,
    "LOCKED_MOUSE": True,
    "DEFAULT_MAP_FILE": "assets/maps/default.json",
    "TEXTURES": {
        "BACKGROUND": "assets/gfx/background.png",
        "SNAKE": "assets/gfx/snake.png",
        "FOOD": "assets/gfx/food.png",
        "BRICK": "assets/gfx/brick.png"
    }
}


class GameError(Exception):
    """Base exception for game-specific errors."""
    pass


class MapSizeError(GameError):
    """Raised when map size doesn't match screen resolution."""
    pass


class AssetNotFoundError(GameError):
    """Raised when a required game asset is missing."""
    pass