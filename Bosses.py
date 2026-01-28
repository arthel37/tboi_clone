import pygame
import math
import Entities 
from Utils import cut_sprite, create_walking_frames as create_face_frames
from pygame.time import get_ticks

def get_boss_stats(name):
    stats = {
        "gurdy_jr": {
            "hp": 20,
            "speed": 3,
            "damage": 2,
            "scale": 3,
            "anim_key": "body",
            "dash_speed": 12,
            "dash_distance": 550,
            "dash_cooldown": 3000,
            "fan_shot_count": 6,
            "fan_angle_range": 90,
            "fan_shot_cooldown": 4000,
        },
    }
    return stats.get(name)

def get_boss_config(assets):
    return {
        "gurdy_jr": {
            "body": cut_sprite(assets['gurdy_jr_sheet'], 0, 0, 96, 90),
            "animated_face": {
                "idle":cut_sprite(assets['gurdy_jr_sheet'], 0, 84, 48, 36),
                "dashing": cut_sprite(assets['gurdy_jr_sheet'], 194, 38, 48, 36),
                "attacking": create_face_frames(
                    sheet=assets['gurdy_jr_sheet'],
                    start_row=1,
                    start_col=2,
                    frame_w=48,
                    frame_h=36,
                    rows=1,
                    cols=3
                )
            }
        }
    }

class Boss(Entities.Entity):
    def __init__(self, game, pos, name="gurdy_jr"):
        self.game = game
        self.name = name
        self.tear_sprite = game.enemies_animations['tear_animations']['enemy']['idle']
        stats = get_boss_stats(name)

        self.hp = stats["hp"]
        self.speed = stats["speed"]
        self.damage = stats["damage"]
        self.scale = stats["scale"]

        self.dash_speed = stats["dash_speed"]
        self.dash_distance = stats["dash_distance"]
        self.dash_cooldown = stats["dash_cooldown"]

        self.fan_count = stats["fan_shot_count"]
        self.fan_angle = stats["fan_angle_range"]
        self.fan_cooldown = stats["fan_shot_cooldown"]

        self.last_dash = 0
        self.last_fan = 0
        self.attacking = False
        self.vel = pygame.Vector2(0,0)

        cfg = get_boss_config(game.assets)[name]
        
        self.body_img = pygame.transform.scale(
            cfg["body"],
            (cfg["body"].get_width()*self.scale, cfg["body"].get_height()*self.scale)
        )
        self.face_idle = pygame.transform.scale(
            cfg["animated_face"]["idle"],
            (cfg["animated_face"]["idle"].get_width()*self.scale,
             cfg["animated_face"]["idle"].get_height()*self.scale)
        )
        self.face_attack_frames = [
            pygame.transform.scale(f, (f.get_width()*self.scale, f.get_height()*self.scale))
            for f in cfg["animated_face"]["attacking"]
        ]
        self.face_dashing = pygame.transform.scale(
            cfg["animated_face"]["dashing"],
            (cfg["animated_face"]["dashing"].get_width() * self.scale,
             cfg["animated_face"]["dashing"].get_height() * self.scale)
        )
        self.face_index = 0
        self.face_timer = 0
        self.face_speed = 50
        self.current_face = self.face_idle

        # INICJALIZACJA ENTITY
        w, h = self.body_img.get_width(), self.body_img.get_height()
        
        # Hitbox mniejszy niż grafika
        hb_w = int(w * 0.7)
        hb_h = int(h * 0.6)
        off_x = (w - hb_w) // 2
        off_y = h - hb_h - 10 # 10px od dołu
        
        super().__init__(game, "enemy", pos, (w, h), 
                         sprite=self.body_img, 
                         hitbox_size=(hb_w, hb_h),
                         hitbox_offset=(off_x, off_y))
        
        self.solid = True

    def move_towards_player(self):
        player = self.game.player
        direction = pygame.Vector2(player.hitbox.center) - pygame.Vector2(self.hitbox.center)
        if direction.length() != 0:
            direction = direction.normalize()
        self.vel = direction * self.speed

    def dash(self):
        now = get_ticks()
        if now - self.last_dash >= self.dash_cooldown:
            self.last_dash = now
            self.dash_remaining_distance = self.dash_distance
            player = self.game.player
            direction = pygame.Vector2(player.hitbox.center) - pygame.Vector2(self.hitbox.center)
            if direction.length() != 0:
                self.dash_dir = direction.normalize()

    def fan_shot(self):
        now = get_ticks()
        if now - self.last_fan >= self.fan_cooldown:
            self.last_fan = now
            self.attacking = True
            self.face_index = 0
            self.face_timer = 0

            center_angle = math.degrees(math.atan2(
                self.game.player.hitbox.centery - self.hitbox.centery,
                self.game.player.hitbox.centerx - self.hitbox.centerx
            ))
            start_angle = center_angle - self.fan_angle / 2
            step = self.fan_angle / (self.fan_count - 1)

            for i in range(self.fan_count):
                angle = math.radians(start_angle + step * i)
                direction = pygame.Vector2(math.cos(angle), math.sin(angle))
                
                # Start pocisku z środka hitboxa
                center_pos = pygame.Vector2(self.hitbox.centerx, self.hitbox.centery)
                
                proj = Entities.Projectile(
                    self.game,
                    center_pos,
                    direction,
                    owner="enemy",
                    damage=self.damage,
                    sprite=self.tear_sprite
                )

                self.game.entities.append(proj)

    def update_face(self, dt):
        if hasattr(self, 'dash_remaining_distance') and self.dash_remaining_distance > 0:
            self.current_face = self.face_dashing
        elif self.attacking:
            self.face_timer += dt
            if self.face_timer >= self.face_speed:
                self.face_timer = 0
                self.face_index += 1
                if self.face_index >= len(self.face_attack_frames):
                    self.face_index = 0
                    self.attacking = False
                    self.current_face = self.face_idle
                else:
                    self.current_face = self.face_attack_frames[self.face_index]
        else:
            self.current_face = self.face_idle

    def update(self, dt):
        self.move_towards_player()
        self.dash()
        self.fan_shot()
        
        move_vec = pygame.Vector2(0,0)
        
        if hasattr(self, 'dash_remaining_distance') and self.dash_remaining_distance > 0:
            step = min(self.dash_speed, self.dash_remaining_distance)
            move_vec = self.dash_dir * step
            self.dash_remaining_distance -= step
        else:
            self.move_towards_player()
            move_vec = self.vel
            
        super().update((move_vec.x, move_vec.y))

        self.update_face(dt)

    def render(self, surf):
        super().render(surf)
        
        face_rect = self.current_face.get_rect(center=(self.pos[0] + self.body_img.get_width() // 2,
                                                       self.pos[1] + self.body_img.get_height() // 2))
        surf.blit(self.current_face, face_rect)
        
        # DEBUG
        pygame.draw.rect(surf, (255, 0, 0), self.hitbox, 1)
        
    def on_collsion_enemy(self, other):
        if hasattr(other, 'owner') and other.owner == 'player':
            self.hp -= other.damage
            print(f'Boss HP={self.hp}')
            if self.hp <= 0 and self in self.game.entities:
                self.game.entities.remove(self)