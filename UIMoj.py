import pygame
from Utils import cut_sprite

class UI:
    def __init__(self, game):
        self.game = game

        heart_full = cut_sprite(
            game.assets['heart_sheet'],
            0, 0,
            16, 16
        )

        self.heart = pygame.transform.scale(heart_full, (16*3, 16*3))
        self.spacing = self.heart.get_width() + 4

    def render(self, surf):
        hp = self.game.player.hp

        for i in range(hp):
            x = 10 + i * self.spacing
            y = 10
            surf.blit(self.heart, (x, y))
