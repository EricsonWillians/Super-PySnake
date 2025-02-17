"""
Main application window and game configuration handling.
"""
import os.path
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict, cast

import pyglet
from pyglet.window import Window, event

from game.types import GameConfig, DEFAULT_CONFIG
from utils.serializable import Serializable, FileOperationError


class ModernConfig(TypedDict):
    """Modern configuration format structure."""
    screen: Dict[str, Any]
    game: Dict[str, Any]
    assets: Dict[str, Any]


class GameWindow(Serializable):
    """Main game window and configuration manager."""
    
    def __init__(
        self, 
        config_path: Optional[Path] = None,
        *,
        verify_assets: bool = True
    ) -> None:
        """Initialize the game window and load configuration."""
        # Initialize Serializable first
        Serializable.__init__(self)
        
        # Initialize config
        self._config: Optional[GameConfig] = None
        self._load_configuration(config_path or Path("config.json"))
        
        if verify_assets:
            self._verify_assets()
            
        # Create the window
        self._window = Window(
            width=self._config["SCREEN_WIDTH"],
            height=self._config["SCREEN_HEIGHT"],
            fullscreen=self._config["FULLSCREEN"],
            caption="Super PySnake"
        )
        
        # Configure window
        if self._config["LOCKED_MOUSE"]:
            self._window.set_exclusive_mouse(True)
            
        # Set window icon
        icon = pyglet.image.load(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "gfx",
                "icon.ico"
            )
        )
        self._window.set_icon(icon)
        
        # Setup event handlers
        self._window.push_handlers(self)

    def _load_configuration(self, config_path: Path) -> None:
        """Load and validate configuration."""
        if config_path.is_file():
            try:
                loaded_config = self.load(config_path)
                self._config = self._transform_config(loaded_config)
            except (FileOperationError, KeyError) as e:
                print(f"Error loading config, using defaults: {e}")
                self._config = DEFAULT_CONFIG.copy()
                # Write the modern format config
                self.data = self._create_modern_config(self._config)
                self.write(config_path)
        else:
            self._config = DEFAULT_CONFIG.copy()
            # Write the modern format config
            self.data = self._create_modern_config(self._config)
            self.write(config_path)

    def _create_modern_config(self, config: GameConfig) -> ModernConfig:
        """Transform internal config format to modern JSON format."""
        return {
            "screen": {
                "width": config["SCREEN_WIDTH"],
                "height": config["SCREEN_HEIGHT"],
                "fullscreen": config["FULLSCREEN"]
            },
            "game": {
                "square_size": config["SQUARE_SIZE"],
                "speed": config["GAME_SPEED"],
                "locked_mouse": config["LOCKED_MOUSE"]
            },
            "assets": {
                "map_file": config["DEFAULT_MAP_FILE"],
                "textures": {
                    "background": config["TEXTURES"]["BACKGROUND"],
                    "snake": config["TEXTURES"]["SNAKE"],
                    "food": config["TEXTURES"]["FOOD"],
                    "brick": config["TEXTURES"]["BRICK"]
                }
            }
        }

    def _transform_config(self, modern_config: Dict[str, Any]) -> GameConfig:
        """Transform modern JSON format to internal config format."""
        try:
            screen = modern_config["screen"]
            game = modern_config["game"]
            assets = modern_config["assets"]
            
            return {
                "SCREEN_WIDTH": screen["width"],
                "SCREEN_HEIGHT": screen["height"],
                "SQUARE_SIZE": game["square_size"],
                "GAME_SPEED": game["speed"],
                "FULLSCREEN": screen["fullscreen"],
                "LOCKED_MOUSE": game["locked_mouse"],
                "DEFAULT_MAP_FILE": assets["map_file"],
                "TEXTURES": {
                    "BACKGROUND": assets["textures"]["background"],
                    "SNAKE": assets["textures"]["snake"],
                    "FOOD": assets["textures"]["food"],
                    "BRICK": assets["textures"]["brick"]
                }
            }
        except KeyError as e:
            raise KeyError(f"Invalid configuration format: missing {e}") from e
        
    @property
    def config(self) -> GameConfig:
        """Get the current configuration."""
        if self._config is None:
            raise RuntimeError("Configuration not initialized")
        return self._config
        
    def _verify_assets(self) -> None:
        """Verify that all required asset files exist."""
        if self._config is None:
            raise RuntimeError("Configuration not initialized")
            
        # Verify texture files
        for texture_name, texture_path in self._config["TEXTURES"].items():
            full_path = Path(texture_path)
            if not full_path.is_file():
                raise FileOperationError(
                    f"Missing texture file for {texture_name}: {texture_path}"
                )
        
        # Verify map file
        map_path = Path(self._config["DEFAULT_MAP_FILE"])
        if not map_path.is_file():
            raise FileOperationError(
                f"Missing default map file: {self._config['DEFAULT_MAP_FILE']}"
            )
    
    @property
    def screen_height(self) -> int:
        """Get the current window height."""
        if self._config is None:
            raise RuntimeError("Configuration not initialized")
        return self._config["SCREEN_HEIGHT"]

    # Delegate pyglet window methods
    def clear(self) -> None:
        """Clear the window."""
        self._window.clear()

    def close(self) -> None:
        """Close the window."""
        self._window.close()

    def event(self, *args) -> Any:
        """Event decorator."""
        return self._window.event(*args)


# Global game window instance
window = GameWindow()