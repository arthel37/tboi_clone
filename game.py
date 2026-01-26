import pygame
import sys
import config
from main_menu import MainMenu
from state_machine import StateMachine
from level import Level

# Klasa gry
class Game:
    def __init__(self, manager):
        self.manager = manager
        self.level_manager = Level(1)

        self.curr_room_coords = (0, 0)
        self.curr_room = self.level_manager.map[self.curr_room_coords]

        ## TEMPORARY PLAyER
        self.player_rect = pygame.Rect(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2, 10, 10)
        self.player_speed = 5

        middle_idx = config.GRID_SIZE // 2
        door_start_idx = middle_idx - 1
        
        door_start_tile_x = config.GRID_OFFSET_X + (door_start_idx * config.TILE_WIDTH)
        door_start_tile_y = config.GRID_OFFSET_Y + (door_start_idx * config.TILE_HEIGHT)
        
        door_width = config.TILE_WIDTH * 3
        door_height = config.TILE_HEIGHT * 3
        
        self.door_top_rect = pygame.Rect(door_start_tile_x, config.GRID_BORDER_TOP - 10, door_width, 10)
        self.door_bottom_rect = pygame.Rect(door_start_tile_x, config.GRID_BORDER_BOTTOM, door_width, 10)
        self.door_left_rect = pygame.Rect(config.GRID_BORDER_LEFT - 10, door_start_tile_y, 10, door_height)
        self.door_right_rect = pygame.Rect(config.GRID_BORDER_RIGHT, door_start_tile_y, 10, door_height)

    def reset(self):
        print('Nowa gra')
        self.level_manager = Level(1)
        self.curr_room_coords = (0, 0)
        self.curr_room = self.level_manager.map[self.curr_room_coords]
        self.player_rect.center = (config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2)

    def update(self):
        keys = pygame.key.get_pressed()

        dx, dy = 0, 0

        if keys[pygame.K_w]:
            dy -= self.player_speed
        if keys[pygame.K_s]:
            dy += self.player_speed
        if keys[pygame.K_a]:
            dx -= self.player_speed
        if keys[pygame.K_d]:
            dx += self.player_speed

        self.player_rect.x += dx
        self.player_rect.y += dy

        if keys[pygame.K_ESCAPE]:
            self.manager.set_state('menu')

        if self.curr_room.doors['top'] and self.player_rect.colliderect(self.door_top_rect):
            self.change_room(0, -1)
            self.player_rect.bottom = config.GRID_BORDER_BOTTOM - 20
            return

        if self.curr_room.doors['bottom'] and self.player_rect.colliderect(self.door_bottom_rect):
            self.change_room(0, 1)
            self.player_rect.top = config.GRID_BORDER_TOP + 20
            return

        if self.curr_room.doors['left'] and self.player_rect.colliderect(self.door_left_rect):
            self.change_room(-1, 0)
            self.player_rect.right = config.GRID_BORDER_RIGHT - 20
            return

        if self.curr_room.doors['right'] and self.player_rect.colliderect(self.door_right_rect):
            self.change_room(1, 0)
            self.player_rect.left = config.GRID_BORDER_LEFT + 20
            return
        
        if self.player_rect.top < config.GRID_BORDER_TOP and not (self.player_rect.left > self.door_top_rect.left and self.player_rect.right < self.door_top_rect.right):
            self.player_rect.top = config.GRID_BORDER_TOP
        
        if self.player_rect.bottom > config.GRID_BORDER_BOTTOM and not (self.player_rect.left > self.door_bottom_rect.left and self.player_rect.right < self.door_bottom_rect.right):
            self.player_rect.bottom = config.GRID_BORDER_BOTTOM
            
        if self.player_rect.left < config.GRID_BORDER_LEFT and not (self.player_rect.top > self.door_left_rect.top and self.player_rect.bottom < self.door_left_rect.bottom):
            self.player_rect.left = config.GRID_BORDER_LEFT
            
        if self.player_rect.right > config.GRID_BORDER_RIGHT and not (self.player_rect.top > self.door_right_rect.top and self.player_rect.bottom < self.door_right_rect.bottom):
            self.player_rect.right = config.GRID_BORDER_RIGHT

    def change_room(self, dx, dy):
        x, y = self.curr_room_coords
        new_coords = (x + dx, y + dy)

        if new_coords in self.level_manager.map:
            self.curr_room_coords = new_coords
            self.curr_room = self.level_manager.map[new_coords]
            self.curr_room.visited = True
        
        print(self.curr_room.info())
    
    def draw(self, surface, room_textures):
        self.curr_room.draw(surface, room_textures)
        pygame.draw.rect(surface, (0, 255, 0), self.player_rect)
        self.draw_minimap(surface)

    def draw_minimap(self, surface):
        minimap_surf = pygame.Surface((config.MINIMAP_WIDTH, config.MINIMAP_HEIGHT), pygame.SRCALPHA)
        
        bg_color = (*config.COLOR_MM_BCKG, config.MINIMAP_ALPHA)
        minimap_surf.fill(bg_color)

        center_x = config.MINIMAP_WIDTH // 2
        center_y = config.MINIMAP_HEIGHT // 2
        
        tile_size = config.MINIMAP_TILE_SIZE
        spacing = 2 

        for coords, room in self.level_manager.map.items():
            room_x, room_y = coords
            curr_x, curr_y = self.curr_room_coords

            diff_x = room_x - curr_x
            diff_y = room_y - curr_y

            draw_x = int(center_x + (diff_x * (tile_size + spacing)) - (tile_size // 2))
            draw_y = int(center_y + (diff_y * (tile_size + spacing)) - (tile_size // 2))

            if coords == self.curr_room_coords:
                color = config.COLOR_MM_CURR
            elif room.visited:
                color = config.COLOR_MM_DISCOVERED
            else:
                color = config.COLOR_MM_UNDISCOVERED

            pygame.draw.rect(minimap_surf, color, (draw_x, draw_y, tile_size, tile_size))

        pygame.draw.rect(minimap_surf, (200, 200, 200), minimap_surf.get_rect(), 2)

        mm_x = config.WINDOW_WIDTH - config.MINIMAP_WIDTH - config.MINIMAP_MARGIN
        mm_y = config.MINIMAP_MARGIN
        surface.blit(minimap_surf, (mm_x, mm_y))

# Metody gry
def create_vignette(width, height):
    print('Tworzenie winiety...')
    vignette = pygame.Surface((width, height), pygame.SRCALPHA)
    vignette.fill((0, 0, 0, 50))
    mask = pygame.Surface((width // 3, height // 3), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    mask = pygame.transform.smoothscale(mask, (width, height))
    vignette.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return vignette

pygame.init()
window_surface = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption('The Binding of Isaac: Ripoff')
clock = pygame.time.Clock()

try:
    print('Ładowanie czcionek...')
    font = pygame.font.Font(config.FONT_PATH, config.FONT_SIZE)
    font_large = pygame.font.Font(config.FONT_PATH, config.FONT_SIZE_LARGE)
except FileNotFoundError as e:
    print(f'Nie znaleziono czcionki {e}')
    font = pygame.font.SysFont('arial', config.FONT_SIZE)
    font_large = pygame.font.SysFont('arial', config.FONT_SIZE_LARGE)

try:
    print('Wczytywanie tekstur...')
    floor_raw = pygame.image.load('images\\tile.png').convert()
    floor_texture = pygame.transform.scale(floor_raw, (config.TILE_WIDTH, config.TILE_HEIGHT))

    wall_raw = pygame.image.load('images\\wall.png').convert()
    wall_texture = pygame.transform.scale(wall_raw, (config.TILE_WIDTH, config.TILE_HEIGHT))

    door_top_raw = pygame.image.load('images\\door_top.png').convert()
    door_top_texture = pygame.transform.scale(door_top_raw, (3 * config.TILE_WIDTH, config.TILE_HEIGHT))

    door_bottom_raw = pygame.image.load('images\\door_bottom.png').convert()
    door_bottom_texture = pygame.transform.scale(door_bottom_raw, (3 * config.TILE_WIDTH, config.TILE_HEIGHT))

    door_left_raw = pygame.image.load('images\\door_left.png').convert()
    door_left_texture = pygame.transform.scale(door_left_raw, (config.TILE_WIDTH, 3 * config.TILE_HEIGHT))

    door_right_raw = pygame.image.load('images\\door_right.png').convert()
    door_right_texture = pygame.transform.scale(door_right_raw, (config.TILE_WIDTH, 3 * config.TILE_HEIGHT))

    room_textures = {
        'floor': floor_texture,
        'wall': wall_texture,
        'door_top': door_top_texture,
        'door_bottom': door_bottom_texture,
        'door_left': door_left_texture,
        'door_right': door_right_texture
    }
except FileNotFoundError as e:
    print(f'Nie odnaleziono pliku {e}')
    pygame.quit()
    sys.exit()

manager = StateMachine()

vignette = create_vignette(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

game_instance = Game(manager)
main_menu = MainMenu(manager)

game_status = True
prev_state = None

while game_status:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            game_status = False
    
    curr_state = manager.get_state()

    if curr_state == 'menu':
        main_menu.update(events)
        main_menu.draw(window_surface, font, font_large)
    elif curr_state == 'game':
        if prev_state != curr_state:
            game_instance.reset()
        game_instance.update()
        game_instance.draw(window_surface, room_textures)
    
    pygame.display.update()
    clock.tick(60)

    prev_state = curr_state

pygame.quit()
sys.exit()