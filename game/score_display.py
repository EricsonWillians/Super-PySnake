import math
import random

import pyglet
from pyglet import clock, image, gl
from pyglet.graphics import Batch
from pyglet.shapes import BorderedRectangle, Circle
from pyglet.text import Label

from game.app import window
from pyscored.adapters.game_frameworks import GameFrameworkAdapter


class ScoreDisplay:
    """
    A modern, Pyglet 2.0-compatible score display panel. Includes:
      - A panel background (optionally from an image, else a BorderedRectangle).
      - A smooth-transitioning main "Score" label with a subtle shadow.
      - A fancy "+XX" increase label that animates in and fades out.
      - Sparkle particles whenever the score increases.
    """

    def __init__(self, adapter: GameFrameworkAdapter, player_id: str):
        self.adapter = adapter
        self.player_id = player_id

        # Internal tracking of actual vs. visual score (for smooth transitions).
        self.current_visual_score = 0
        self.target_score = 0

        # Keep track of old score to detect changes
        self.last_score = 0
        self.score_changed = False

        # For timing/animations
        self.time = 0

        # We'll store particles as data only, and dynamically create Circle shapes in _draw_particles().
        self.particles = []

        # Create a Pyglet batch so multiple labels are drawn in one pass.
        self.batch = Batch()

        # Panel dimensions + position
        screen_width = window.config["SCREEN_WIDTH"]
        screen_height = window.config["SCREEN_HEIGHT"]
        self.panel_width = 300
        self.panel_height = 50
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = screen_height - self.panel_height - 32  # 15px from top

        # Attempt to load a custom background image; if not found, use a shape-based panel
        try:
            self.bg_image = image.load('assets/score_bg.png')
        except (FileNotFoundError, pyglet.resource.ResourceNotFoundException):
            self.bg_image = None

        # Main label shadow
        self.shadow_label = Label(
            text="Score: 0",
            font_name="Arial Bold",
            font_size=20,
            x=self.panel_x + self.panel_width // 2 + 2,  # +2 offset for a "shadow"
            y=self.panel_y + self.panel_height // 2 - 2,
            anchor_x="center",
            anchor_y="center",
            color=(0, 0, 0, 100),  # Semi-transparent black
            batch=self.batch
        )

        # Main label (white, on top)
        self.label = Label(
            text="Score: 0",
            font_name="Arial Bold",
            font_size=20,
            x=self.panel_x + self.panel_width // 2,
            y=self.panel_y + self.panel_height // 2,
            anchor_x="center",
            anchor_y="center",
            color=(255, 255, 255, 255),
            batch=self.batch
        )

        # Score-increase indicator (default invisible)
        self.increase_label = Label(
            text="",
            font_name="Arial Bold",
            font_size=16,
            x=self.panel_x + self.panel_width - 10,
            y=self.panel_y + self.panel_height // 2,
            anchor_x="left",   # We'll position it to the right of the main label
            anchor_y="center",
            color=(255, 220, 0, 0),
            batch=self.batch
        )

        # Schedule our _animate function at ~60fps
        clock.schedule_interval(self._animate, 1 / 60.0)

    def _animate(self, dt: float) -> None:
        """
        Main animation loop for:
          - Smoothly interpolating score changes
          - Pulsing the main label color
          - Handling the "increase" label and sparkles
        """
        self.time += dt

        # Smoothly move current_visual_score toward target_score
        if self.current_visual_score != self.target_score:
            diff = (self.target_score - self.current_visual_score)
            self.current_visual_score += diff * min(dt * 5, 1)
            if abs(self.current_visual_score - self.target_score) < 0.5:
                self.current_visual_score = self.target_score

            # Update main labels
            score_text = f"Score: {int(self.current_visual_score)}"
            self.label.text = score_text
            self.shadow_label.text = score_text

        # If the score just changed, show the increase label and create particles
        if self.score_changed:
            increase = self.target_score - self.last_score
            if increase > 0:
                self.increase_label.text = f"+{int(increase)}"
                self.increase_label.color = (255, 220, 0, 255)

                # Generate up to 10 sparkles
                for _ in range(min(int(increase), 10)):
                    self._add_particle()

                # Schedule fade-out after 1 second
                clock.schedule_once(self._fade_increase_label, 1.0)

            self.score_changed = False

        # Subtle pulsing color effect on the main label
        pulse = 0.8 + 0.2 * math.sin(self.time * 2)
        self.label.color = (
            int(255 - 40 * pulse),
            int(255 - 20 * pulse),
            255,
            255
        )

        # Reposition the increase label so it sits just to the right of the main label
        self._position_increase_label()

        # Update all particles
        for particle in list(self.particles):
            particle["life"] -= dt
            if particle["life"] <= 0:
                self.particles.remove(particle)
                continue

            # Move + gravity
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["vy"] -= 50 * dt  # Gravity
            # Alpha fades over time
            particle["alpha"] = 255 * (particle["life"] / particle["max_life"])

    def _position_increase_label(self) -> None:
        """
        Place the increase_label just to the right of the main label's text,
        so the two never overlap.
        """
        # Center x of main label plus half the text width, plus a small gap
        gap = 14
        label_right = self.label.x + (self.label.content_width / 2)
        self.increase_label.x = label_right + gap
        self.increase_label.y = self.label.y

    def _fade_increase_label(self, dt: float) -> None:
        """
        Called ~1s after a score increment to schedule a gradual fade out
        for the "increase_label."
        """
        def _fade_step(_):
            alpha = self.increase_label.color[3] - 10
            if alpha <= 0:
                self.increase_label.color = (255, 220, 0, 0)
                clock.unschedule(_fade_step)
                return
            self.increase_label.color = (255, 220, 0, alpha)

        clock.schedule_interval(_fade_step, 1 / 30.0)

    def _add_particle(self) -> None:
        """Generate a sparkle particle near the 'increase_label' area."""
        self.particles.append({
            "x": self.increase_label.x + random.randint(-5, 15),
            "y": self.increase_label.y + random.randint(-5, 5),
            "vx": random.uniform(-20, 20),
            "vy": random.uniform(10, 40),
            "size": random.uniform(2, 4),
            "color": (255, 220, 0),
            "life": random.uniform(0.5, 1.5),
            "max_life": 1.5,
            "alpha": 255
        })

    def update(self) -> None:
        """
        Check the latest score from the game adapter. If there's a change,
        mark it so we can animate in _animate().
        """
        new_score = self.adapter.get_player_score(self.player_id)
        if new_score != self.target_score:
            self.last_score = self.target_score
            self.target_score = new_score
            self.score_changed = True

    def _draw_particles(self) -> None:
        """
        Draw each particle as a small pyglet.shapes.Circle.
        This avoids immediate-mode calls and is fully compatible with pyglet 2.0.
        """
        for p in self.particles:
            circle = Circle(
                x=p["x"],
                y=p["y"],
                radius=p["size"],
                color=(p["color"][0], p["color"][1], p["color"][2]),
            )
            circle.opacity = int(p["alpha"])
            circle.draw()

    def draw(self) -> None:
        """
        Called once per frame to draw the score panel, labels, and particles.
        (Likely called in your main on_draw handler.)
        """
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # If a custom image background is available, use it
        if self.bg_image:
            self.bg_image.blit(self.panel_x, self.panel_y)
        else:
            # Otherwise, draw a simple, partially transparent rectangle
            panel = BorderedRectangle(
                x=self.panel_x,
                y=self.panel_y,
                width=self.panel_width,
                height=self.panel_height,
                border=2,
                color=(38, 38, 46),       # Darkish gray
                border_color=(100, 100, 110)
            )
            panel.opacity = 200
            panel.draw()

        # Draw sparkle particles behind the label text
        self._draw_particles()

        # Finally, draw all text labels
        self.batch.draw()
