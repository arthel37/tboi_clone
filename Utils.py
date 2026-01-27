import pygame
import sys
import Entities

BASE_IMG_PATH='data/images/'

key_to_index_move = {
    pygame.K_d: 0,
    pygame.K_a: 1,
    pygame.K_w: 2,
    pygame.K_s: 3
}

key_to_index_shoot = {
    pygame.K_RIGHT: 0,
    pygame.K_LEFT: 1,
    pygame.K_UP: 2,
    pygame.K_DOWN: 3
}


def EventHandlingMoj(movement, shooting):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            state = event.type == pygame.KEYDOWN

            if event.key in key_to_index_move:
                movement[key_to_index_move[event.key]] = state
            if event.key in key_to_index_shoot:
                shooting[key_to_index_shoot[event.key]] = state

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH+path).convert_alpha()
    return img

def cut_sprite(sheet, x, y, w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.blit(sheet, (0, 0), (x, y, w, h))
    return surf
def create_walking_frames(sheet, start_row, start_col, frame_w, frame_h, rows, cols):
    frames = []
    for r in range(rows):
        for c in range(cols):
            x = (start_col + c) * frame_w
            y = (start_row + r) * frame_h
            frames.append(cut_sprite(sheet, x, y, frame_w, frame_h))
    return frames

def spawn_enemy(game, type_name, pos, scale=3, anim_key=None):
    if anim_key is None:
        anim_key = f"{type_name}_head"
    enemy = Entities.Enemy(game, pos, type_name=type_name, scale=scale, anim_key=anim_key)
    game.entities.append(enemy)
    return enemy

def spawn_boss(game, name, pos):
    from Bosses import Boss
    boss = Boss(game=game, pos=pos, name=name)
    game.entities.append(boss)
    return boss