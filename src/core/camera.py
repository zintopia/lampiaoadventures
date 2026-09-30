"""
Smooth Camera System with Level Boundary Clamping.
"""

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, LEVEL_WIDTH, LEVEL_HEIGHT

class Camera:
    def __init__(self, width: int = LEVEL_WIDTH, height: int = LEVEL_HEIGHT):
        self.camera_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.width = width
        self.height = height
        self.lerp_speed = 0.08  # Smoothness factor for movement interpolation

    def update(self, target_rect: pygame.Rect):
        """Update camera target tracking smoothly centered on target_rect."""
        target_x = target_rect.centerx - SCREEN_WIDTH // 2
        target_y = target_rect.centery - SCREEN_HEIGHT // 2

        # Linear interpolation (lerp) for smooth camera tracking
        self.camera_rect.x += int((target_x - self.camera_rect.x) * self.lerp_speed)
        self.camera_rect.y += int((target_y - self.camera_rect.y) * self.lerp_speed)

        # Clamp camera to level boundaries
        self.camera_rect.x = max(0, min(self.camera_rect.x, self.width - SCREEN_WIDTH))
        self.camera_rect.y = max(0, min(self.camera_rect.y, self.height - SCREEN_HEIGHT))

    def apply(self, entity_or_rect) -> pygame.Rect:
        """Translates world rect to screen coordinates."""
        if hasattr(entity_or_rect, 'rect'):
            rect = entity_or_rect.rect
        else:
            rect = entity_or_rect
        return rect.move(-self.camera_rect.x, -self.camera_rect.y)

    def apply_point(self, x: float, y: float) -> tuple:
        """Translates world coordinate point to screen coordinates."""
        return (x - self.camera_rect.x, y - self.camera_rect.y)
