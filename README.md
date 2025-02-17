# Super PySnake 🐍

A modern implementation of the classic Snake game using Pyglet, featuring smooth graphics and a highly modular architecture.

![License](https://img.shields.io/badge/license-GPL--2.0-blue.svg)
![Python](https://img.shields.io/badge/python-^3.8-blue.svg)
![Pyglet](https://img.shields.io/badge/pyglet-^2.0.0-green.svg)

## 🎮 Features

- Smooth, OpenGL-accelerated graphics
- Modern Python practices and type hints
- Configurable game settings
- Custom map support
- Pixel-perfect collision detection
- Fullscreen support

## 🚀 Quick Start

1. Ensure you have Poetry installed:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone and install:
```bash
git clone https://github.com/ericsonwillians/Super-PySnake.git
cd Super-PySnake
poetry install
```

3. Run the game:
```bash
poetry run super-pysnake
```

## 🎯 Controls

- Arrow keys or WASD to move
- ESC to quit

## 🏗️ Project Structure

```
super_pysnake/
├── .gitignore
├── README.md
├── pyproject.toml
├── config.json
├── assets/
│   ├── gfx/
│   │   ├── background.png
│   │   ├── brick.png
│   │   ├── food.png
│   │   ├── icon.ico
│   │   └── snake.png
│   └── maps/
│       └── default.json
└── game/
    ├── __init__.py
    ├── app.py
    ├── types.py
    ├── dungeon.py
    ├── food.py
    ├── snake.py
    ├── square.py
    ├── utils/
    │   ├── __init__.py
    │   └── serializable.py
    └── main.py
```

## ⚙️ Configuration

The game can be configured through `config.json`:

```json
{
    "screen": {
        "width": 1024,
        "height": 768,
        "fullscreen": false
    },
    "game": {
        "square_size": 32,
        "speed": 0.1,
        "locked_mouse": true
    },
    "assets": {
        "map_file": "assets/maps/default.json",
        "textures": {
            "background": "assets/gfx/background.png",
            "snake": "assets/gfx/snake.png",
            "food": "assets/gfx/food.png",
            "brick": "assets/gfx/brick.png"
        }
    }
}
```

## 🎨 Custom Maps

Create custom maps by editing the JSON map file. The map format uses:
- `1` for walls
- `0` for empty spaces

Example:
```json
{
    "map": [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1]
    ]
}
```

## 🛠️ Development

This project uses:
- Poetry for dependency management
- Type hints throughout
- Modern Python features
- Modular architecture

For development:
```bash
# Install dev dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Lint
poetry run pylint game/
```

## 📝 License

Copyright © 2015-2025 Ericson Willians

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

## ✨ Acknowledgments

Original Super PySnake game created by Ericson Willians in 2015. This modern refactor maintains the original game's charm while bringing it up to date with current Python practices and technologies.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

We welcome:
- Bug fixes
- Feature additions
- Documentation improvements
- Code optimization
- Test coverage improvements