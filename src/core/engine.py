"""
Game Engine.
Initializes Pygame subsystem, window display, game clock, and main execution loop.
"""

import sys
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, COLOR_BACKGROUND
from src.core.scene_manager import SceneManager
from src.core.audio_manager import AudioManager

class Engine:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"[Engine] Warning: Could not initialize mixer: {e}")

        pygame.font.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()
        self.running = False
        self.fps = FPS

        self.scene_manager = SceneManager()
        self.audio_manager = AudioManager()

    def run(self):
        """Main game loop."""
        self.running = True
        while self.running:
            # Calculate delta time (dt in seconds)
            dt = self.clock.tick(self.fps) / 1000.0

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # Delegate event handling, update, and rendering to active scene
            self.scene_manager.handle_events(events)
            self.scene_manager.update(dt)

            self.screen.fill(COLOR_BACKGROUND)
            self.scene_manager.render(self.screen)

            pygame.display.flip()

        self.quit()

    def quit(self):
        pygame.quit()
        sys.exit()
