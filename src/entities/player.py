"""
Player Entity.
Implements platformer movement, jumping, sprinting with stamina management,
health & invulnerability, and interaction triggers.
"""

import pygame
from config import (
    COLOR_PLAYER, GRAVITY, MAX_FALL_SPEED, PLAYER_SPEED, PLAYER_SPRINT_SPEED,
    PLAYER_JUMP_FORCE, MAX_HEALTH, MAX_STAMINA, STAMINA_DRAIN, STAMINA_RECHARGE,
    KEY_LEFT, KEY_RIGHT, KEY_JUMP, KEY_SPRINT, KEY_INTERACT
)
from src.entities.base_entity import BaseEntity
from src.core.audio_manager import AudioManager

class Player(BaseEntity):
    def __init__(self, x: float, y: float):
        super().__init__(
            x=x, y=y, width=38, height=58,
            color=COLOR_PLAYER, label="LAMPIÃO",
            sprite_path="assets/sprites/player/lampiao.png"
        )
        self.health = MAX_HEALTH
        self.max_health = MAX_HEALTH

        self.stamina = MAX_STAMINA
        self.max_stamina = MAX_STAMINA
        self.is_sprinting = False
        self.is_exhausted = False

        self.coins_collected = 0
        self.invulnerable_timer = 0.0
        self.invulnerable_duration = 1.0  # seconds

        # Movement fine-tuning
        self.coyote_timer = 0.0
        self.coyote_time_max = 0.15  # grace period after walking off edges
        self.jump_buffer = 0.0
        self.jump_buffer_max = 0.15

        self.audio_manager = AudioManager()
        self.interact_pressed = False

    def handle_input(self, events):
        """Processes key presses for jump buffer and interaction trigger."""
        self.interact_pressed = False
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_JUMP:
                    self.jump_buffer = self.jump_buffer_max
                if event.key in KEY_INTERACT:
                    self.interact_pressed = True

    def update(self, dt: float, tiles: list):
        if not self.is_active:
            return

        keys = pygame.key.get_pressed()

        # Handle Invulnerability Timer
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        # Sprint logic & Stamina Drain / Recharge
        sprint_requested = any(keys[k] for k in KEY_SPRINT)
        moving_horizontally = any(keys[k] for k in KEY_LEFT) or any(keys[k] for k in KEY_RIGHT)

        if sprint_requested and moving_horizontally and not self.is_exhausted and self.stamina > 0:
            self.is_sprinting = True
            self.stamina = max(0.0, self.stamina - STAMINA_DRAIN)
            if self.stamina <= 0:
                self.is_exhausted = True
                self.is_sprinting = False
        else:
            self.is_sprinting = False
            if self.stamina < self.max_stamina:
                self.stamina = min(self.max_stamina, self.stamina + STAMINA_RECHARGE)
                if self.is_exhausted and self.stamina >= 25.0:
                    self.is_exhausted = False  # Recovered enough stamina to sprint again

        # Horizontal Movement Speed
        current_speed = PLAYER_SPRINT_SPEED if self.is_sprinting else PLAYER_SPEED

        # Direction Input
        self.vel.x = 0
        if any(keys[k] for k in KEY_LEFT):
            self.vel.x = -current_speed
            self.facing = "left"
        if any(keys[k] for k in KEY_RIGHT):
            self.vel.x = current_speed
            self.facing = "right"

        # Horizontal Position Update & Collision Resolution
        self.pos.x += self.vel.x
        self.update_rect()
        for tile in tiles:
            if tile.is_solid and self.rect.colliderect(tile.rect):
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                elif self.vel.x < 0:
                    self.rect.left = tile.rect.right
                self.pos.x = self.rect.x

        # Gravity & Jump Timers
        if self.is_grounded:
            self.coyote_timer = self.coyote_time_max
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)

        if self.jump_buffer > 0:
            self.jump_buffer = max(0.0, self.jump_buffer - dt)

        # Execute Jump if buffer and ground/coyote available
        if self.jump_buffer > 0 and self.coyote_timer > 0:
            self.vel.y = PLAYER_JUMP_FORCE
            self.is_grounded = False
            self.coyote_timer = 0
            self.jump_buffer = 0
            self.audio_manager.play_sfx("assets/audio/sfx/jump.wav")

        # Apply Gravity
        self.vel.y += GRAVITY
        if self.vel.y > MAX_FALL_SPEED:
            self.vel.y = MAX_FALL_SPEED

        # Vertical Position Update & Collision Resolution
        self.pos.y += self.vel.y
        self.update_rect()
        self.is_grounded = False

        for tile in tiles:
            if tile.is_solid and self.rect.colliderect(tile.rect):
                if self.vel.y > 0:  # Falling down onto surface
                    self.rect.bottom = tile.rect.top
                    self.vel.y = 0
                    self.is_grounded = True
                elif self.vel.y < 0:  # Hitting ceiling
                    self.rect.top = tile.rect.bottom
                    self.vel.y = 0
                self.pos.y = self.rect.y

    def take_damage(self, amount: int):
        """Reduces HP and applies invulnerability frames."""
        if self.invulnerable_timer <= 0 and self.health > 0:
            self.health = max(0, self.health - amount)
            self.invulnerable_timer = self.invulnerable_duration
            self.audio_manager.play_sfx("assets/audio/sfx/hurt.wav")
            # Slight recoil boost upwards
            self.vel.y = -6.0

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def render(self, screen: pygame.Surface, camera):
        """Render player with visual flicker during invulnerability."""
        if not self.is_active:
            return

        # Flicker effect when invulnerable
        if self.invulnerable_timer > 0:
            if int(self.invulnerable_timer * 15) % 2 == 0:
                return

        super().render(screen, camera)
