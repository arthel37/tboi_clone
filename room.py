import pygame
import config

class Room:
    def __init__(self, x, y, room_type='normal'):
        print('Tworzenie obiektu pokoju...')
        self.x = x
        self.y = y
        self.room_type = room_type
        self.distance = 0

        self.doors = {
            'top': False,
            'bottom': False,
            'left': False,
            'right': False
        }

    def draw(self, surface, textures):
        wall = textures['wall']
        for row in range(config.GRID_SIZE):
            x1 = 0
            x2 = config.WINDOW_WIDTH - config.GRID_OFFSET_X
            y = config.WALL_VERT_THICKNESS + (row * config.TILE_HEIGHT)
            surface.blit(wall, (x1, y))
            surface.blit(wall, (x2, y))
        for col in range(config.GRID_SIZE + 2):
            x = 0 + (col * config.TILE_WIDTH)
            y1 = 0
            y2 = config.WINDOW_HEIGHT - config.GRID_OFFSET_Y
            surface.blit(wall, (x, y1))
            surface.blit(wall, (x, y2))


        floor = textures['floor']
        for row in range(config.GRID_SIZE):
            for col in range(config.GRID_SIZE):
                x = config.WALL_HORIZ_THICKNESS + (col * config.TILE_WIDTH)
                y = config.WALL_VERT_THICKNESS + (row * config.TILE_HEIGHT)
                surface.blit(floor, (x, y))

        center_x = config.WINDOW_WIDTH // 2
        center_y = config.WINDOW_HEIGHT // 2

        if self.doors['top']:
            x = center_x - config.TILE_WIDTH
            y = 0
            surface.blit(textures['door_top'], (x, y))

        if self.doors['bottom']:
            x = center_x - config.TILE_WIDTH
            y = config.WINDOW_HEIGHT - config.WALL_VERT_THICKNESS
            surface.blit(textures['door_bottom'], (x, y))

        if self.doors['left']:
            x = 0
            y = center_y - config.TILE_HEIGHT
            surface.blit(textures['door_left'], (x, y))

        if self.doors['right']:
            x = config.WINDOW_WIDTH - config.WALL_HORIZ_THICKNESS
            y = center_y - config.TILE_HEIGHT
            surface.blit(textures['door_right'], (x, y))

    def info(self):
        return f'Room ({self.x, self.y}) - {self.room_type} | Doors: {self.doors}'