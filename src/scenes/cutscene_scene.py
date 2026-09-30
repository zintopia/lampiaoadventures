"""
Cutscene Scene Framework.
Plays intro/story cutscenes with animated props and sequential dialogue pages scaled for virtual resolution.
"""

import math
import pygame
from config import VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_WHITE, KEY_CONFIRM
from src.scenes.base_scene import BaseScene
from src.ui.dialogue_box import DialogueBox
from src.utils.asset_loader import AssetLoader
from src.core.audio_manager import AudioManager

class CutsceneScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.dialogue_box = DialogueBox()
        self.audio_manager = AudioManager()
        self.next_scene = "LEVEL_1"
        self.anim_timer = 0.0

        self.prop_surf = AssetLoader.load_image(
            relative_path="assets/sprites/props/cutscene_intro.png",
            size=(140, 100),
            fallback_color=(204, 119, 34),
            label="JUMENTO VOADOR"
        )
        self.font_skip = pygame.font.SysFont("arial", 9, italic=True)

    def on_enter(self, **kwargs):
        self.next_scene = kwargs.get("next_scene", "LEVEL_1")
        self.anim_timer = 0.0
        self.audio_manager.play_music("assets/audio/music/cutscene_theme.wav")

        intro_dialogues = [
            "No coração do Sertão de Canudos, a lendária gatinha 'Catita' desapareceu!",
            "Os cabras do Cangaço espalharam mistérios e cactos por toda a caatinga.",
            "Lampião assume seu chapéu de couro e sua bravura para resgatar a Catita!",
            "Prepare-se para a grande aventura no Sertão!"
        ]

        self.dialogue_box.start_dialogue(
            speaker_name="NARRADOR DO SERTÃO",
            pages=intro_dialogues,
            on_complete=self.finish_cutscene,
            portrait_label="CORDEL"
        )

    def finish_cutscene(self):
        if self.scene_manager:
            self.scene_manager.change_scene(self.next_scene)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.finish_cutscene()
                    return

        self.dialogue_box.handle_events(events)

    def update(self, dt: float):
        self.anim_timer += dt
        self.dialogue_box.update(dt)

    def render(self, screen: pygame.Surface):
        screen.fill((255, 160, 100))

        prop_y = int(90 + math.sin(self.anim_timer * 3.0) * 8.0)
        p_rect = self.prop_surf.get_rect(center=(VIRTUAL_WIDTH // 2, prop_y))
        screen.blit(self.prop_surf, p_rect)

        skip_txt = self.font_skip.render("Pressione [ESC] para Pular Cutscene", True, COLOR_WHITE)
        screen.blit(skip_txt, (VIRTUAL_WIDTH - 155, 10))

        self.dialogue_box.render(screen)
