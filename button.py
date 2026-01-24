import pygame
import config

class Button:
    def __init__(self, text: str, x: int, y: int, width: int, height: int, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

    def draw(self, surface, is_selected, font, font_large):
        # Rysowanie prostokąta z ramką 
        # Efekt powiększenia
        if is_selected:
            current_font = font_large
            color = config.COLOR_TEXT_SELECTED
        else:
            current_font = font
            color = config.COLOR_TEXT_DESELECT

        text_surf = current_font.render(self.text, True, color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)