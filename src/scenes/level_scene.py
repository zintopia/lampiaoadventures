"""
Level Scene (Gameplay).
Integrates Player, LevelManager, Smooth Camera, HUD, and NPC Dialogue system.
"""

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_BLACK, COLOR_STAMINA_YELLOW, KEY_PAUSE
from src.scenes.base_scene import BaseScene
from src.entities.player import Player
from src.level.level_manager import LevelManager
from src.core.camera import Camera
from src.ui.hud import HUD
from src.ui.dialogue_box import DialogueBox
from src.core.audio_manager import AudioManager

class LevelScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.audio_manager = AudioManager()
        self.hud = HUD()
        self.dialogue_box = DialogueBox()
        self.is_paused = False
        self.game_over = False

        self.font_overlay = pygame.font.SysFont("arial", 36, bold=True)
        self.font_sub = pygame.font.SysFont("arial", 20)

    def on_enter(self, **kwargs):
        """Initializes fresh Level 1 state."""
        self.level_manager = LevelManager()
        spawn_x, spawn_y = self.level_manager.player_spawn
        self.player = Player(spawn_x, spawn_y)
        self.camera = Camera()
        self.is_paused = False
        self.game_over = False
        self.audio_manager.play_music("assets/audio/music/sertao_theme.wav")

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_PAUSE:
                    self.is_paused = not self.is_paused

                if self.game_over or self.level_manager.level_completed:
                    if event.key in [pygame.K_r, pygame.K_RETURN, pygame.K_SPACE]:
                        # Restart Level
                        self.on_enter()
                    elif event.key == pygame.K_ESCAPE:
                        # Return to Menu
                        if self.scene_manager:
                            self.scene_manager.change_scene("MENU")

        # Delegate events to dialogue box if modal, else to player
        if self.dialogue_box.is_active:
            self.dialogue_box.handle_events(events)
        elif not self.is_paused and not self.game_over:
            self.player.handle_input(events)

    def update(self, dt: float):
        if self.is_paused or self.game_over:
            return

        if self.dialogue_box.is_active:
            self.dialogue_box.update(dt)
            return

        # Player death check
        if self.player.health <= 0:
            self.game_over = True
            return

        # Level finish check
        if self.level_manager.level_completed:
            return

        # Update player physics & movement
        self.player.update(dt, self.level_manager.solid_tiles)

        # Update level (enemies, collectibles, hazards)
        self.level_manager.update(dt, self.player)

        # Smooth camera target tracking centered on player
        self.camera.update(self.player.rect)

        # NPC Interaction Check
        for npc in self.level_manager.npcs:
            if npc.is_player_near(self.player):
                if self.player.interact_pressed:
                    self.dialogue_box.start_dialogue(
                        speaker_name=npc.name,
                        pages=npc.dialogue_pages,
                        portrait_label=npc.label
                    )
                    self.player.interact_pressed = False
                    break

    def render(self, screen: pygame.Surface):
        # Sertão Sky Background
        screen.fill((255, 218, 185))

        # Render level geometry, props, hazards, collectibles, NPCs, enemies
        self.level_manager.render(screen, self.camera)

        # Render player
        self.player.render(screen, self.camera)

        # Render NPC floating interaction prompts if near player
        if not self.dialogue_box.is_active:
            for npc in self.level_manager.npcs:
                if npc.is_player_near(self.player):
                    npc.render_prompt(screen, self.camera)

        # Render HUD Top-Left Overlay
        self.hud.render(screen, self.player)

        # Render Modal Dialogue Box if active
        if self.dialogue_box.is_active:
            self.dialogue_box.render(screen)

        # Render Game Over Overlay
        if self.game_over:
            self._render_overlay(screen, "GAME OVER!", "Você tombou no sertão. Pressione [R] para Tentar Novamente ou [ESC] para Menu.")

        # Render Level Completed Overlay
        elif self.level_manager.level_completed:
            self._render_overlay(screen, "VILA FINAL ALCANÇADA!", f"Parabéns! Você resgatou a Catita com {self.player.coins_collected} moedas! Pressione [R] para Jogar Novamente.")

        # Render Pause Overlay
        elif self.is_paused:
            self._render_overlay(screen, "JOGO PAUSADO", "Pressione [ESC] ou [P] para Continuar.")

    def _render_overlay(self, screen: pygame.Surface, title: str, subtitle: str):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 200))
        screen.blit(overlay, (0, 0))

        title_txt = self.font_overlay.render(title, True, COLOR_STAMINA_YELLOW)
        t_rect = title_txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(title_txt, t_rect)

        sub_txt = self.font_sub.render(subtitle, True, COLOR_WHITE)
        s_rect = sub_txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25))
        screen.blit(sub_txt, s_rect)
