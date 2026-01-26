import pygame
import config

class Room:
    def __init__(self, x, y, room_type='normal'):
        self.x = x
        self.y = y
        self.room_type = room_type
        self.distance = 0
        self.visited = True if self.x == 0 and self.y == 0 else False

        self.doors = {
            'top': False,
            'bottom': False,
            'left': False,
            'right': False
        }

    def draw(self, surface, textures):
        wall = textures['wall']
        floor = textures['floor']
        
        for row in range(config.GRID_SIZE):
            for col in range(config.GRID_SIZE):
                x = config.GRID_OFFSET_X + (col * config.TILE_WIDTH)
                y = config.GRID_OFFSET_Y + (row * config.TILE_HEIGHT)
                surface.blit(floor, (x, y))

        for col in range(-1, config.GRID_SIZE + 1):
            x = config.GRID_OFFSET_X + (col * config.TILE_WIDTH)
            y_top = config.GRID_OFFSET_Y - config.TILE_HEIGHT
            surface.blit(wall, (x, y_top))
            
            y_bottom = config.GRID_OFFSET_Y + (config.GRID_SIZE * config.TILE_HEIGHT)
            surface.blit(wall, (x, y_bottom))

        for row in range(config.GRID_SIZE):
            y = config.GRID_OFFSET_Y + (row * config.TILE_HEIGHT)
            
            x_left = config.GRID_OFFSET_X - config.TILE_WIDTH
            surface.blit(wall, (x_left, y))
            
            x_right = config.GRID_OFFSET_X + (config.GRID_SIZE * config.TILE_WIDTH)
            surface.blit(wall, (x_right, y))

        middle_idx = config.GRID_SIZE // 2
        door_start_idx = middle_idx - 1

        if self.doors['top']:
            x = config.GRID_OFFSET_X + (door_start_idx * config.TILE_WIDTH)
            y = config.GRID_OFFSET_Y - config.TILE_HEIGHT
            surface.blit(textures['door_top'], (x, y))

        if self.doors['bottom']:
            x = config.GRID_OFFSET_X + (door_start_idx * config.TILE_WIDTH)
            y = config.GRID_OFFSET_Y + (config.GRID_SIZE * config.TILE_HEIGHT)
            surface.blit(textures['door_bottom'], (x, y))

        if self.doors['left']:
            x = config.GRID_OFFSET_X - config.TILE_WIDTH
            y = config.GRID_OFFSET_Y + (door_start_idx * config.TILE_HEIGHT)
            surface.blit(textures['door_left'], (x, y))

        if self.doors['right']:
            x = config.GRID_OFFSET_X + (config.GRID_SIZE * config.TILE_WIDTH)
            y = config.GRID_OFFSET_Y + (door_start_idx * config.TILE_HEIGHT)
            surface.blit(textures['door_right'], (x, y))
            
    def info(self):
        return f'Room ({self.x, self.y}) - {self.room_type} | Doors: {self.doors}'