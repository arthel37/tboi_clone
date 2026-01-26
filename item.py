import pygame

class Item:
    def __init__(self, id, name, texture_path, stat_change=None, modifier=None):
        self.id = id
        self.name = name
        
        try:
            self.image = pygame.image.load(texture_path).convert_alpha()
        except FileNotFoundError as e:
            print(f'Nie odnaleziono pliku: {e}')
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 255))

        self.rect = self.image.get_rect()

        self.stat_change = stat_change if stat_change else {}
        self.modifier = modifier

    