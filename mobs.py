import pygame
from Utils import cut_sprite, create_walking_frames
def get_player_config(assets):

    head_right_idle = cut_sprite(assets['player_sheet'], 64, 0, 32, 32)
    head_right_shooting = cut_sprite(assets['player_sheet'], 96, 0, 32, 32)
    body_right_idle = cut_sprite(assets['player_sheet'], 0, 32, 32, 32)
    body_right_walking = create_walking_frames(
        sheet=assets['player_sheet'],
        start_row=2,
        start_col=0,
        frame_w=32,
        frame_h=32,
        rows=1,
        cols=8
    )


    head_left_idle = pygame.transform.flip(head_right_idle, True, False)
    head_left_shooting = pygame.transform.flip(head_right_shooting, True, False)
    body_left_idle = pygame.transform.flip(body_right_idle, True, False)
    body_left_walking = [pygame.transform.flip(frame, True, False) for frame in body_right_walking]

    return {
        "head": {
            "down": {
                "idle": cut_sprite(assets['player_sheet'], 0, 0, 32, 32),
                "shooting": cut_sprite(assets['player_sheet'], 32, 0, 32, 32),
            },
            "right": {
                "idle": head_right_idle,
                "shooting": head_right_shooting,
            },
            "left": {
                "idle": head_left_idle,
                "shooting": head_left_shooting,
            },
            "up": {
                "idle": cut_sprite(assets['player_sheet'], 128, 0, 32, 32),
                "shooting": cut_sprite(assets['player_sheet'], 160, 0, 32, 32),
            }
        },
        "body": {
            "down": {
                "idle": cut_sprite(assets['player_sheet'], 0, 32, 32, 32),
                "walking": create_walking_frames(
                    sheet=assets['player_sheet'],
                    start_row=1,
                    start_col=0,
                    frame_w=32,
                    frame_h=32,
                    rows=1,
                    cols=8
                )
            },
            "right": {
                "idle": body_right_idle,
                "walking": body_right_walking
            },
            "left": {
                "idle": body_left_idle,
                "walking": body_left_walking
            },
            "up": {
                "idle": cut_sprite(assets['player_sheet'], 0, 32, 32, 32),
                "walking": create_walking_frames(
                    sheet=assets['player_sheet'],
                    start_row=0,
                    start_col=6,
                    frame_w=32,
                    frame_h=32,
                    rows=1,
                    cols=2
                )
            }
        }
    }

def get_mobs_config(assets):
    return {
        "zombie": {
            "zombie_head": {
                "idle": cut_sprite(assets['zombie_head_sheet'], 0, 0, 32, 32),
                "aggro": cut_sprite(assets['zombie_head_sheet'], 32, 0, 32, 32),
            },
            "zombie_legs": {
                "idle": cut_sprite(assets['zombie_legs_sheet'], 0, 0, 32, 32),
                "walking": create_walking_frames(
                    sheet=assets['zombie_legs_sheet'],
                    start_row=0,
                    start_col=1,
                    frame_w=32,
                    frame_h=32,
                    rows=2,
                    cols=3
                )
            }
        },
        "fly": {
            "fly_head": {
                "aggro": [
                    cut_sprite(assets['fly'], 0, 0, 32, 32),
                    cut_sprite(assets['fly'], 32, 0, 32, 32)
                ]
            }
        },
        "tear_animations": {
            "player": {
                "idle": cut_sprite(assets['tear_sheet'], 0, 0, 64, 64)
            },
            "enemy": {
                "idle": cut_sprite(assets['blood_tear_sheet'], 0, 0, 64, 64)
            }
        }
    }
def get_mobs_stats():
    return {
        "player": {
            "hp": 6,
            "speed": 10,
            "damage": 2.5,
            "shoot_cooldown": 400,
            "scale": 3,

        },
        "zombie": {
            "hp": 8,
            "speed": 4,
            "damage": 1,
            "shoot_cooldown": 4000,
            "scale": 3,
            "anim_key": "zombie_head",
        },
        "fly": {
            "hp": 3,
            "speed": 0.3,
            "damage": 1,
            "shoot_cooldown": 2000,
            "scale": 3,
            "anim_key": "fly_head",
        },
    }
