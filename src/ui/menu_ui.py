"""
Main Menu UI Component.
Renders main menu title, animated backlands aesthetic elements, and interactive option buttons.
"""

import math
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_BLACK, COLOR_STAMINA_YELLOW,
    COLOR_SUN, COLOR_GROUND, COLOR_DIALOGUE_BG, COLOR_DIALOGUE_BORDER
)

class MenuButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False
        self.font = pygame.font.SysFont("arial", 22, bold=True)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def render(self, screen: pygame.Surface):
        bg_color = (200, 100, 30) if self.is_hovered else (40, 40, 45)
        border_color = COLOR_STAMINA_YELLOW if self.is_hovered else (100, 100, 100)
        
        # Shadow
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(screen, (20, 20, 20), shadow_rect, border_radius=8)

        # Button Body
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, border_color, self.rect, width=3, border_radius=8)

        # Text
        txt_color = COLOR_WHITE if self.is_hovered else (220, 220, 220)
        txt_surf = self.font.render(self.text, True, txt_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

class MenuUI:
    def __init__(self, start_callback, quit_callback):
        self.start_callback = start_callback
        self.quit_callback = quit_callback

        self.font_title = pygame.font.SysFont("arial", 48, bold=True)
        self.font_subtitle = pygame.font.SysFont("arial", 22, italic=True)
        self.font_footer = pygame.font.SysFont("arial", 14)

        btn_w, btn_h = 280, 56
        center_x = SCREEN_WIDTH // 2 - btn_w // 2

        self.buttons = [
            MenuButton(center_x, 340, btn_w, btn_h, "[1] INICIAR JOGO", start_callback),
            MenuButton(center_x, 420, btn_w, btn_h, "[2] SAIR DO JOGO", quit_callback)
        ]

        self.selected_idx = 0
        self.anim_timer = 0.0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in self.buttons:
                    if btn.is_hovered:
                        btn.action()

            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_RETURN, pygame.K_SPACE]:
                    self.buttons[0].action()
                elif event.key in [pygame.K_2, pygame.K_ESCAPE]:
                    self.buttons[1].action()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected_idx = (self.selected_idx - 1) % len(self.buttons)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected_idx = (self.selected_idx + 1) % len(self.buttons)

    def update(self, dt: float):
        self.anim_timer += dt
        mouse_pos = pygame.mouse.get_pos()
        for i, btn in enumerate(self.buttons):
            btn.update(mouse_pos)
            if i == self.selected_idx and not any(b.rect.collidepoint(mouse_pos) for b in self.buttons):
                btn.is_hovered = True

    def render(self, screen: pygame.Surface):
        # Sertão Sky & Sun background decoration
        screen.fill((255, 218, 185))
        
        # Sun
        sun_y = int(220 + math.sin(self.anim_timer * 0.8) * 10)
        pygame.draw.circle(screen, COLOR_SUN, (SCREEN_WIDTH // 2, sun_y), 140)

        # Ground silhouette
        pygame.draw.rect(screen, COLOR_GROUND, (0, 560, SCREEN_WIDTH, 160))

        # Title Card Panel
        title_box = pygame.Rect(SCREEN_WIDTH // 2 - 380, 70, 760, 180)
        bg_surf = pygame.Surface((title_box.width, title_box.height), pygame.SRCALPHA)
        bg_surf.fill((20, 20, 25, 220))
        screen.blit(bg_surf, title_box.topleft)
        pygame.draw.rect(screen, COLOR_DIALOGUE_BORDER, title_box, width=3, border_radius=12)

        # Main Title
        title_txt = self.font_title.render("LAMPIÃO ADVENTURES", True, COLOR_STAMINA_YELLOW)
        shadow_txt = self.font_title.render("LAMPIÃO ADVENTURES", True, COLOR_BLACK)
        t_rect = title_txt.get_rect(center=(SCREEN_WIDTH // 2, 130))
        screen.blit(shadow_txt, (t_rect.x + 3, t_rect.y + 3))
        screen.blit(title_txt, t_rect)

        # Subtitle
        sub_txt = self.font_subtitle.render("A Busca da Catita Perdida no Sertão", True, COLOR_WHITE)
        sub_rect = sub_txt.get_rect(center=(SCREEN_WIDTH // 2, 190))
        screen.blit(sub_txt, sub_rect)

        # Buttons
        for btn in self.buttons:
            btn.render(screen)

        # Footer instructions
        footer_txt = self.font_footer.render("Use MOUSE ou TECLAS [1] / [2] / [ENTER] para navegar", True, COLOR_WHITE)
        f_rect = footer_txt.get_rect(center=(SCREEN_WIDTH // 2, 680))
        screen.blit(footer_txt, f_rect)
