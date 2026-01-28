import pygame
import config

class Room:
    def __init__(self, x, y, room_type='normal'):
        self.x = x
        self.y = y
        self.room_type = room_type
        self.distance = 0
        self.visited = True if self.x == 0 and self.y == 0 else False
        self.cleared = False
        
        if self.room_type in ['shop', 'item', 'start']:
            self.cleared = True

        self.doors = {
            'top': False,
            'bottom': False,
            'left': False,
            'right': False
        }

    def draw(self, surface, textures):
        wall_top = textures['wall_top']
        wall_bottom = textures['wall_bottom']
        wall_left = textures['wall_left']
        wall_right = textures['wall_right']
        floor = textures['floor']
        
        for row in range(config.GRID_SIZE):
            for col in range(config.GRID_SIZE):
                x = config.GRID_OFFSET_X + (col * config.TILE_WIDTH)
                y = config.GRID_OFFSET_Y + (row * config.TILE_HEIGHT)
                surface.blit(floor, (x, y))

        surface.blit(wall_top, (0, 0))
        surface.blit(wall_bottom, (0, config.WINDOW_HEIGHT - wall_bottom.get_height()))
        surface.blit(wall_left, (0, 0))
        surface.blit(wall_right, (config.WINDOW_WIDTH - wall_right.get_width(), 0))

        middle_idx = config.GRID_SIZE // 2
        door_start_idx = middle_idx - 1

        if self.doors['top']:
            x = config.GRID_OFFSET_X + (door_start_idx * config.TILE_WIDTH)
            surface.blit(textures['door_top'], (x, config.GRID_BORDER_TOP - config.TILE_HEIGHT))

        if self.doors['bottom']:
            x = config.GRID_OFFSET_X + (door_start_idx * config.TILE_WIDTH)
            surface.blit(textures['door_bottom'], (x, config.GRID_BORDER_BOTTOM))

        if self.doors['left']:
            y = config.GRID_OFFSET_Y + (door_start_idx * config.TILE_HEIGHT)
            surface.blit(textures['door_left'], (config.GRID_BORDER_LEFT - config.TILE_WIDTH, y))

        if self.doors['right']:
            y = config.GRID_OFFSET_Y + (door_start_idx * config.TILE_HEIGHT)
            surface.blit(textures['door_right'], (config.GRID_BORDER_RIGHT, y))
            
    def info(self):
        return f'Room ({self.x, self.y}) - {self.room_type} | Cleared: {self.cleared}'