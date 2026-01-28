import pygame
import sys
import config
import random
import Entities
from Entities import Pickup, Trapdoor
from Bosses import Boss 
from Utils import load_image, EventHandlingMoj, spawn_enemy, spawn_boss
from mobs import get_mobs_config, get_player_config
from UIMoj import UI
from main_menu import MainMenu
from state_machine import StateMachine
from level import Level

class Game:
    def __init__(self, manager):
        self.manager = manager
        self.floor_num = 1
        self.max_floors = 8
        
        self.assets = {
            'player_sheet':load_image('isaac/character_isaac.png'),
            'zombie_head_sheet':load_image('enemies/zombie_head.png'),
            'zombie_legs_sheet':load_image('enemies/zombie_legs.png'),
            'fly':load_image('enemies/fly.png'),
            'tear_sheet':load_image('tears/tear.png'),
            'blood_tear_sheet':load_image('tears/bloodtear.png'),
            'heart_sheet':load_image('ui/hearts.png'),
            'gurdy_jr_sheet': load_image('bosses/gurdyjr.png'),
            'trapdoor': load_image('room_tiles/trapdoor.png') 
        }

        self.isaac_animations = get_player_config(self.assets)
        self.enemies_animations = get_mobs_config(self.assets)
        
        self.player = Entities.Player(self, (config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
        self.ui = UI(self)
        
        self.init_level(1)

        #HITBOXY DRZWI
        
        middle_idx = config.GRID_SIZE // 2
        door_start_idx = middle_idx - 1
        
        door_start_tile_x = config.GRID_OFFSET_X + (door_start_idx * config.TILE_WIDTH)
        door_start_tile_y = config.GRID_OFFSET_Y + (door_start_idx * config.TILE_HEIGHT)
        
        door_width = config.TILE_WIDTH * 3
        door_height = config.TILE_HEIGHT * 3
        
        door_thickness = 30

        self.door_top_rect = pygame.Rect(door_start_tile_x, config.GRID_BORDER_TOP - door_thickness - 10, door_width, door_thickness)
        
        self.door_bottom_rect = pygame.Rect(door_start_tile_x, config.GRID_BORDER_BOTTOM + 10, door_width, door_thickness)
        
        self.door_left_rect = pygame.Rect(config.GRID_BORDER_LEFT - door_thickness - 10, door_start_tile_y, door_thickness, door_height)
        
        self.door_right_rect = pygame.Rect(config.GRID_BORDER_RIGHT + 10, door_start_tile_y, door_thickness, door_height)

    def init_level(self, level_num):
        self.level_manager = Level(level_num)
        self.curr_room_coords = (0, 0)
        self.curr_room = self.level_manager.map[self.curr_room_coords]
        self.curr_room.visited = True
        self.curr_room.cleared = True 

        self.movement = [False, False, False, False]
        self.shooting = [False, False, False, False]
        
        self.entities = [self.player]
        self.player.set_pos(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2)

    def next_level(self):
        self.floor_num += 1
        if self.floor_num > self.max_floors:
            print("YOU WON THE GAME!")
            self.manager.set_state('menu')
            return
            
        print(f"Advancing to Level {self.floor_num}")
        self.init_level(self.floor_num)

    def reset(self):
        print('New Game')
        self.floor_num = 1
        self.player = Entities.Player(self, (config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
        self.init_level(1)

    def update(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_ESCAPE]:
            self.manager.set_state('menu')
        
        enemies_alive = [e for e in self.entities if isinstance(e, Entities.Enemy) or isinstance(e, Boss)]
        
        if not self.curr_room.cleared and len(enemies_alive) == 0:
            self.on_room_cleared()

        if self.curr_room.cleared:
            if self.curr_room.doors['top'] and self.player.hitbox.colliderect(self.door_top_rect):
                self.change_room(0, -1)
                self.player.set_pos(self.player.pos[0], config.GRID_BORDER_BOTTOM - self.player.size[1] - 20)
                return
            
            if self.curr_room.doors['bottom'] and self.player.hitbox.colliderect(self.door_bottom_rect):
                self.change_room(0, 1)
                self.player.set_pos(self.player.pos[0], config.GRID_BORDER_TOP)
                return
            
            if self.curr_room.doors['left'] and self.player.hitbox.colliderect(self.door_left_rect):
                self.change_room(-1, 0)
                self.player.set_pos(config.GRID_BORDER_RIGHT - self.player.size[0], self.player.pos[1])
                return
            
            if self.curr_room.doors['right'] and self.player.hitbox.colliderect(self.door_right_rect):
                self.change_room(1, 0)
                self.player.set_pos(config.GRID_BORDER_LEFT, self.player.pos[1])
                return
        
    def on_room_cleared(self):
        self.curr_room.cleared = True
        print("Room Cleared!")
        
        center_pos = (config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2)

        if self.curr_room.room_type not in ['shop', 'item', 'boss']:
            if random.random() < 0.9:
                self.entities.append(Pickup(self, center_pos))
        
        if self.curr_room.room_type == 'boss':
             self.entities.append(Trapdoor(self, center_pos))

    def change_room(self, dx, dy):
        x, y = self.curr_room_coords
        new_coords = (x + dx, y + dy)

        if new_coords in self.level_manager.map:
            self.curr_room_coords = new_coords
            self.curr_room = self.level_manager.map[new_coords]
            self.curr_room.visited = True
            
            self.entities = [self.player]
            
            if not self.curr_room.cleared:
                self.spawn_room_content()
        
        print(self.curr_room.info())

    def spawn_room_content(self):
        rtype = self.curr_room.room_type
        
        if rtype == 'normal':
            if random.random() < 0.9:
                num_enemies = random.randint(2, 4 + self.floor_num)
                for _ in range(num_enemies):
                    ex = random.randint(config.GRID_BORDER_LEFT + 50, config.GRID_BORDER_RIGHT - 50)
                    ey = random.randint(config.GRID_BORDER_TOP + 50, config.GRID_BORDER_BOTTOM - 50)
                    etype = random.choice(['zombie', 'fly'])
                    spawn_enemy(self, etype, (ex, ey))
            else:
                self.curr_room.cleared = True
                
        elif rtype == 'boss':
            center_x = config.WINDOW_WIDTH // 2 - 50 
            center_y = config.WINDOW_HEIGHT // 2 - 50
            spawn_boss(self, "gurdy_jr", (center_x, center_y))
            
        elif rtype in ['shop', 'item']:
            self.curr_room.cleared = True

    def draw(self, surface, room_textures):
        self.curr_room.draw(surface, room_textures)
        self.draw_minimap(surface)
        
        # DEBUG: Wizualizacja drzwi
        color = (0, 255, 0)
        if self.curr_room.doors['top']: pygame.draw.rect(surface, color, self.door_top_rect, 2)
        if self.curr_room.doors['bottom']: pygame.draw.rect(surface, color, self.door_bottom_rect, 2)
        if self.curr_room.doors['left']: pygame.draw.rect(surface, color, self.door_left_rect, 2)
        if self.curr_room.doors['right']: pygame.draw.rect(surface, color, self.door_right_rect, 2)


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
                if room.room_type == 'boss':
                    color = (150, 0, 0)
                elif room.room_type == 'item':
                    color = (255, 215, 0)
                elif room.room_type == 'shop':
                    color = (0, 200, 0)
                else:
                    color = config.COLOR_MM_DISCOVERED
            else:
                color = config.COLOR_MM_UNDISCOVERED

            pygame.draw.rect(minimap_surf, color, (draw_x, draw_y, tile_size, tile_size))

        pygame.draw.rect(minimap_surf, (200, 200, 200), minimap_surf.get_rect(), 2)
        mm_x = config.WINDOW_WIDTH - config.MINIMAP_WIDTH - config.MINIMAP_MARGIN
        mm_y = config.MINIMAP_MARGIN
        surface.blit(minimap_surf, (mm_x, mm_y))

pygame.init()
window_surface = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption('The Binding of Isaac: Ripoff')
clock = pygame.time.Clock()

try:
    font = pygame.font.Font(config.FONT_PATH, config.FONT_SIZE)
    font_large = pygame.font.Font(config.FONT_PATH, config.FONT_SIZE_LARGE)
except Exception:
    font = pygame.font.SysFont('arial', config.FONT_SIZE)
    font_large = pygame.font.SysFont('arial', config.FONT_SIZE_LARGE)

try:
    print('Wczytywanie tekstur...')
    floor_raw = pygame.image.load('data/images/room_tiles/tile.png').convert()
    floor_texture = pygame.transform.scale(floor_raw, (config.TILE_WIDTH, config.TILE_HEIGHT))

    wall_raw = pygame.image.load('data/images/room_tiles/wall.png').convert()
    
    top_h = config.GRID_OFFSET_Y
    bottom_h = config.WINDOW_HEIGHT - (config.GRID_OFFSET_Y + config.FLOOR_HEIGHT_PX)
    left_w = config.GRID_OFFSET_X
    right_w = config.WINDOW_WIDTH - (config.GRID_OFFSET_X + config.FLOOR_WIDTH_PX)

    wall_top = pygame.transform.scale(wall_raw, (config.WINDOW_WIDTH, top_h))
    wall_bottom = pygame.transform.scale(wall_raw, (config.WINDOW_WIDTH, bottom_h))
    wall_left = pygame.transform.scale(wall_raw, (left_w, config.WINDOW_HEIGHT)) 
    wall_right = pygame.transform.scale(wall_raw, (right_w, config.WINDOW_HEIGHT))

    door_top_raw = pygame.image.load('data/images/doors/door_top.png').convert_alpha()
    door_top_texture = pygame.transform.scale(door_top_raw, (3 * config.TILE_WIDTH, config.TILE_HEIGHT))

    door_bottom_raw = pygame.image.load('data/images/doors/door_bottom.png').convert_alpha()
    door_bottom_texture = pygame.transform.scale(door_bottom_raw, (3 * config.TILE_WIDTH, config.TILE_HEIGHT))

    door_left_raw = pygame.image.load('data/images/doors/door_left.png').convert_alpha()
    door_left_texture = pygame.transform.scale(door_left_raw, (config.TILE_WIDTH, 3 * config.TILE_HEIGHT))

    door_right_raw = pygame.image.load('data/images/doors/door_right.png').convert_alpha()
    door_right_texture = pygame.transform.scale(door_right_raw, (config.TILE_WIDTH, 3 * config.TILE_HEIGHT))

    room_textures = {
        'floor': floor_texture,
        'wall_top': wall_top,
        'wall_bottom': wall_bottom,
        'wall_left': wall_left,
        'wall_right': wall_right,
        'door_top': door_top_texture,
        'door_bottom': door_bottom_texture,
        'door_left': door_left_texture,
        'door_right': door_right_texture
    }
except FileNotFoundError as e:
    print(f'Error loading textures: {e}')
    pygame.quit()
    sys.exit()

manager = StateMachine()
game_instance = Game(manager)
main_menu = MainMenu(manager, game_instance)

game_status = True

while game_status:
    events = pygame.event.get()
    tick = clock.tick(config.FPS)

    for event in events:
        if event.type == pygame.QUIT:
            game_status = False
    
    curr_state = manager.get_state()

    if curr_state == 'menu':
        main_menu.update(events)
        main_menu.draw(window_surface, font, font_large)
    elif curr_state == 'game':

        game_instance.update()
        game_instance.draw(window_surface, room_textures)
        EventHandlingMoj(events, game_instance.movement, game_instance.shooting)

        for e in game_instance.entities.copy():
            if isinstance(e, Entities.Enemy) or isinstance(e, Boss):
                e.update(tick)
            else:
                e.update()
            
            if e not in game_instance.entities:
                continue

            if not isinstance(e, Entities.Player):
                e.render(window_surface)

        game_instance.player.update(game_instance.movement, game_instance.shooting, tick)
        game_instance.player.render(window_surface)
        game_instance.ui.render(window_surface)
    
    pygame.display.update()

pygame.quit()
sys.exit()