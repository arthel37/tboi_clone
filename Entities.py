import pygame
import config
from mobs import get_mobs_stats

class Entity:
    def __init__(self, game, e_type, pos, size, sprite=None, hitbox_size=None, hitbox_offset=None):
        self.game = game
        self.type = e_type
        self.pos = list(pos) 
        self.size = size 
        self.velocity = [0, 0]
        self.sprite = sprite
        
        if hitbox_size:
            self.hitbox_size = hitbox_size
        else:
            self.hitbox_size = size

        if hitbox_offset:
            self.hitbox_offset = list(hitbox_offset)
        else:
            self.hitbox_offset = [
                (size[0] - self.hitbox_size[0]) // 2,
                size[1] - self.hitbox_size[1]
            ]

        self.hitbox = pygame.Rect(
            self.pos[0] + self.hitbox_offset[0], 
            self.pos[1] + self.hitbox_offset[1], 
            self.hitbox_size[0], 
            self.hitbox_size[1]
        )

        self.mask = None
        if self.sprite:
            self.mask = pygame.mask.from_surface(self.sprite)
        self.solid = False

    def sync_hitbox_to_pos(self):
        self.hitbox.x = self.pos[0] + self.hitbox_offset[0]
        self.hitbox.y = self.pos[1] + self.hitbox_offset[1]

    def sync_pos_to_hitbox(self):
        self.pos[0] = self.hitbox.x - self.hitbox_offset[0]
        self.pos[1] = self.hitbox.y - self.hitbox_offset[1]

    def update(self, movement=(0, 0)):
        self.pos[0] += movement[0] + self.velocity[0]
        self.sync_hitbox_to_pos()
        
        self.check_damage_collision()
        
        if self.check_solid_collision():
            self.pos[0] -= movement[0] + self.velocity[0]
            self.sync_hitbox_to_pos()
        
        self.check_wall_collision('x')

        self.pos[1] += movement[1] + self.velocity[1]
        self.sync_hitbox_to_pos()
        
        if self.check_solid_collision():
            self.pos[1] -= movement[1] + self.velocity[1]
            self.sync_hitbox_to_pos()
            
        self.check_wall_collision('y')

    def check_wall_collision(self, axis):
        if self.type == 'projectile':
            return

        doors = self.game.curr_room.doors
        cleared = self.game.curr_room.cleared
        
        door_center_x = (config.GRID_BORDER_LEFT + config.GRID_BORDER_RIGHT) // 2
        door_center_y = (config.GRID_BORDER_TOP + config.GRID_BORDER_BOTTOM) // 2
        
        door_width = config.TILE_WIDTH * 3
        door_height = config.TILE_HEIGHT * 3
        
        is_player = (self.type == 'player')
        
        updated = False
        can_pass = False
        
        if axis == 'x':
            if self.hitbox.left < config.GRID_BORDER_LEFT:
                if cleared and doors['left'] and is_player:
                    if abs(self.hitbox.centery - door_center_y) < (door_height // 2) - 5:
                        can_pass = True
                if not can_pass:
                    self.hitbox.left = config.GRID_BORDER_LEFT
                    updated = True
            elif self.hitbox.right > config.GRID_BORDER_RIGHT:
                if cleared and doors['right'] and is_player:
                    if abs(self.hitbox.centery - door_center_y) < (door_height // 2) - 5:
                        can_pass = True
                if not can_pass:
                    self.hitbox.right = config.GRID_BORDER_RIGHT
                    updated = True
        elif axis == 'y':
            if self.hitbox.top < config.GRID_BORDER_TOP:
                if cleared and doors['top'] and is_player:
                    if abs(self.hitbox.centerx - door_center_x) < (door_width // 2) - 5:
                        can_pass = True
                if not can_pass:
                    self.hitbox.top = config.GRID_BORDER_TOP
                    updated = True
            elif self.hitbox.bottom > config.GRID_BORDER_BOTTOM:
                if cleared and doors['bottom'] and is_player:
                    if abs(self.hitbox.centerx - door_center_x) < (door_width // 2) - 5:
                        can_pass = True
                if not can_pass:
                    self.hitbox.bottom = config.GRID_BORDER_BOTTOM
                    updated = True
        
        if updated:
            self.sync_pos_to_hitbox()

    def render(self, surf):
        if self.sprite:
            surf.blit(self.sprite, self.pos)
            # DEBUG HITBOXA
            pygame.draw.rect(surf, (255, 0, 0), self.hitbox, 1)

    def check_solid_collision(self):
        for entity in self.game.entities:
            if entity is self:
                continue
            if not getattr(entity, "solid", False) and entity.type not in ['player', 'enemy', 'boss']: 
                 continue
            if self.hitbox.colliderect(entity.hitbox):
                return True
        return False

    def check_damage_collision(self):
        pass

    def on_collsion_enemy(self, enemy):
        pass


class Player(Entity):
    def __init__(self, game, pos, scale=3):
        stats = get_mobs_stats()['player']
        self.hp = stats["hp"]
        self.max_hp = 20
        self.speed = stats["speed"]
        self.damage = stats["damage"]
        self.scale = stats["scale"]
        self.shoot_cooldown = stats["shoot_cooldown"]
        self.facing_dir = 'down'
        self.head_facing = 'down'
        self.head_state = 'idle'
        
        self.head_animations = {}
        for dir_name, states in game.isaac_animations['head'].items():
            self.head_animations[dir_name] = {}
            for state, sprite in states.items():
                if isinstance(sprite, list):
                    self.head_animations[dir_name][state] = [
                        pygame.transform.scale(frame, (frame.get_width() * scale, frame.get_height() * scale)) for frame in sprite
                    ]
                else:
                    self.head_animations[dir_name][state] = pygame.transform.scale(
                        sprite, (sprite.get_width() * scale, sprite.get_height() * scale)
                    )

        self.body_animations = {}
        for dir_name, states in game.isaac_animations['body'].items():
            self.body_animations[dir_name] = {}
            for state, sprite in states.items():
                if isinstance(sprite, list):
                    self.body_animations[dir_name][state] = [
                        pygame.transform.scale(frame, (frame.get_width() * scale, frame.get_height() * scale)) for frame in sprite
                    ]
                else:
                    self.body_animations[dir_name][state] = pygame.transform.scale(
                        sprite, (sprite.get_width() * scale, sprite.get_height() * scale)
                    )

        self.legs_index = 0
        self.legs_timer = 0
        self.legs_speed = 100

        head_idle = self.head_animations['down']['idle']
        if isinstance(head_idle, list):
            head_idle = head_idle[0]
        
        w, h = head_idle.get_width(), head_idle.get_height()
        
        # HITBOX GRACZA
        hb_w, hb_h = 30, 30
        off_x = (w - hb_w) // 2
        off_y = h - hb_h // 2

        super().__init__(game, 'player', pos, 
                         (w, h), 
                         head_idle,
                         hitbox_size=(hb_w, hb_h),
                         hitbox_offset=(off_x, off_y)) 
        
        self.solid = True 
        self.tear_sprite = game.enemies_animations['tear_animations']['player']['idle']
        self.mask = pygame.mask.from_surface(head_idle)

        self.last_shot = 0
        self.invincible = False
        self.invincible_time = 1000
        self.last_hit_time = 0

    def update(self, movement=None, shooting=None, dt=0):
        dx = dy = 0
        moving = False

        if movement:
            if movement[0]: dx += self.speed; self.facing_dir = 'right'; moving = True
            if movement[1]: dx -= self.speed; self.facing_dir = 'left'; moving = True
            if movement[2]: dy -= self.speed; self.facing_dir = 'up'; moving = True
            if movement[3]: dy += self.speed; self.facing_dir = 'down'; moving = True

        super().update((dx, dy))

        for entity in self.game.entities:
            if isinstance(entity, Pickup):
                if self.hitbox.colliderect(entity.hitbox):
                    entity.on_pickup(self)
            elif isinstance(entity, Trapdoor):
                if self.hitbox.colliderect(entity.hitbox):
                    entity.on_enter(self)

        shooting_dir = None
        if shooting:
            shooting_dir = self.get_shoot_direction(shooting)

        if shooting_dir:
            self.head_state = 'shooting'
            self.head_facing = self.get_dir_from_vector(shooting_dir)

            now = pygame.time.get_ticks()
            if not hasattr(self, 'last_shot'):
                self.last_shot = 0
            if now - self.last_shot >= self.shoot_cooldown:
                self.last_shot = now
                self.shoot(shooting_dir)
        else:
            self.head_state = 'idle'
            if moving:
                self.head_facing = self.facing_dir

        self.body_state = 'walking' if moving else 'idle'
        self.body_facing = self.facing_dir

        if self.body_state == 'walking' and 'walking' in self.body_animations[self.body_facing]:
            self.legs_timer += dt
            if self.legs_timer >= self.legs_speed:
                self.legs_timer = 0
                self.legs_index = (self.legs_index + 1) % len(self.body_animations[self.body_facing]['walking'])

        if self.invincible:
            now = pygame.time.get_ticks()
            if now - self.last_hit_time >= self.invincible_time:
                self.invincible = False

    def get_dir_from_vector(self, vec):
        x, y = vec
        if abs(x) > abs(y):
            return 'right' if x > 0 else 'left'
        else:
            return 'down' if y > 0 else 'up'

    def get_shoot_direction(self, shooting):
        if shooting[0]: return (1, 0) 
        if shooting[1]: return (-1, 0)
        if shooting[2]: return (0, -1)
        if shooting[3]: return (0, 1)
        return None

    def shoot(self, direction):
        bullet_estimate_size = 30
        
        spawn_x = self.hitbox.centerx - 2 * bullet_estimate_size
        spawn_y = self.hitbox.centery - 2 * bullet_estimate_size

        bullet = Projectile(
            self.game,
            (spawn_x, spawn_y),
            direction,
            damage=self.damage,
            owner='player',
            sprite=self.tear_sprite
        )
        self.game.entities.append(bullet)

    def die(self):
        print("Player dead")
        self.game.manager.set_state('menu') 

    def check_damage_collision(self):
        for entity in self.game.entities:
            if entity is self:
                continue
            elif entity.type == 'enemy':
                if self.hitbox.colliderect(entity.hitbox):
                    self.on_collsion_enemy(entity)
        pass 

    def on_collsion_enemy(self, enemy):
        if self.invincible:
            return

        self.hp -= enemy.damage
        self.invincible = True
        self.last_hit_time = pygame.time.get_ticks()

        if self.hp <= 0:
            self.die()

    def render(self, surf):
        if self.invincible:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return

        body_frames = self.body_animations[self.body_facing]
        if self.body_state == 'walking' and 'walking' in body_frames:
            frames = body_frames['walking']
            frame = frames[self.legs_index % len(frames)]
        else:
            frame = body_frames['idle']

        # Rysowanie ciała względem pozycji sprite'a
        body_pos = (self.pos[0], self.pos[1] + self.head_animations[self.head_facing][self.head_state].get_height()//2 - 10)
        surf.blit(frame, body_pos)

        head_frame = self.head_animations[self.head_facing][self.head_state]
        if isinstance(head_frame, list):
            head_frame = head_frame[0]
        surf.blit(head_frame, self.pos)
        
        # DEBUG
        pygame.draw.rect(surf, (0, 255, 0), self.hitbox, 1)

    def set_pos(self, x, y):
        self.pos[0] = x
        self.pos[1] = y
        self.sync_hitbox_to_pos()

class Enemy(Entity):
    def __init__(self, game, pos, type_name="zombie", scale=3, anim_key="zombie_head"):
        self.tear_sprite = game.enemies_animations['tear_animations']['enemy']['idle']
        stats = get_mobs_stats()[type_name]
        self.hp = stats["hp"]
        self.speed = stats["speed"]
        self.damage = stats["damage"]
        self.scale = stats["scale"]
        self.anim_key = stats["anim_key"]
        self.shoot_cooldown = stats["shoot_cooldown"]

        anims = game.enemies_animations[type_name][anim_key]
        head_frames = anims["aggro"]
        if isinstance(head_frames, list):
            self.head_frames = []
            for frame in head_frames:
                w, h = frame.get_width(), frame.get_height()
                frame = pygame.transform.scale(frame, (w * scale, h * scale))
                self.head_frames.append(frame)
            self.head_index = 0
            self.head_timer = 0
            self.head_speed = 200
            self.head_sprite = self.head_frames[0]
        else:
            w, h = head_frames.get_width(), head_frames.get_height()
            self.head_sprite = pygame.transform.scale(head_frames, (w * scale, h * scale))
            self.head_frames = None

        legs_anims = game.enemies_animations[type_name].get(type_name + "_legs", {})
        self.legs_frames = legs_anims.get("walking", [])
        scaled_legs = []
        for frame in self.legs_frames:
            w, h = frame.get_width(), frame.get_height()
            scaled_legs.append(pygame.transform.scale(frame, (w * scale, h * scale)))
        self.legs_frames = scaled_legs

        self.legs_index = 0
        self.legs_timer = 0
        self.legs_speed = 100

        total_width = self.head_sprite.get_width()
        total_height = self.head_sprite.get_height()
        if self.legs_frames:
            total_height += self.legs_frames[0].get_height()

        # HITBOXY PRZECIWNIKÓW
        hb_w, hb_h = 40, 40
        
        if type_name == "fly":
            # Mucha: Hitbox wyśrodkowany
            off_x = (total_width - hb_w) // 2
            off_y = (total_height - hb_h) // 2
        else:
            # Gaper/Zombie: Hitbox na dole
            # Podciągamy go lekko do góry (-5), żeby nie był "pod" spritem
            off_x = (total_width - hb_w) // 2
            off_y = total_height - 3 * hb_h 

        super().__init__(game, "enemy", pos, 
                         (total_width, total_height), 
                         self.head_sprite,
                         hitbox_size=(hb_w, hb_h),
                         hitbox_offset=(off_x, off_y))
        
        self.mask = pygame.mask.from_surface(self.head_sprite)
        self.solid = True
        self.last_shot = 0

    def update(self, dt=0):
        player = self.game.player
        if not player:
            return

        # Idź do hitboxa gracza
        dx = player.hitbox.centerx - self.hitbox.centerx
        dy = player.hitbox.centery - self.hitbox.centery
        mag = (dx ** 2 + dy ** 2) ** 0.5
        if mag != 0:
            dx /= mag
            dy /= mag
        
        move_x = dx * self.speed
        move_y = dy * self.speed
        
        super().update((move_x, move_y))

        if hasattr(self, 'try_shoot_at_player'):
            self.try_shoot_at_player()

        if self.head_frames:
            self.head_timer += dt
            if self.head_timer >= self.head_speed:
                self.head_timer = 0
                self.head_index = (self.head_index + 1) % len(self.head_frames)
                self.head_sprite = self.head_frames[self.head_index]

        if self.legs_frames:
            self.legs_timer += dt
            if self.legs_timer >= self.legs_speed:
                self.legs_timer = 0
                self.legs_index = (self.legs_index + 1) % len(self.legs_frames)

    def render(self, surf):
        if self.legs_frames:
            body_image = self.legs_frames[self.legs_index]
            body_pos = (self.pos[0], self.pos[1] + self.head_sprite.get_height()//2 -10)
            surf.blit(body_image, body_pos)
        surf.blit(self.head_sprite, self.pos)
        
        # DEBUG
        pygame.draw.rect(surf, (255, 0, 0), self.hitbox, 1)

    def try_shoot_at_player(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_cooldown:
            return

        player = self.game.player
        if not player:
            return

        px, py = player.hitbox.center
        ex, ey = self.hitbox.center
        dx = px - ex
        dy = py - ey
        if dx == 0 and dy == 0:
            return

        mag = (dx ** 2 + dy ** 2) ** 0.5
        dir_vector = (dx / mag, dy / mag)

        bullet_pos = (
            self.hitbox.centerx - 10,
            self.hitbox.centery - 20
        )

        bullet = Projectile(
            self.game,
            bullet_pos,
            dir_vector,
            damage=self.damage,
            owner="enemy",
            sprite=self.tear_sprite
        )
        self.game.entities.append(bullet)
        self.last_shot = now

    def on_collsion_enemy(self, other):
        if hasattr(other, 'owner') and other.owner == 'player':
             self.hp -= other.damage
             if self.hp <= 0 and self in self.game.entities:
                self.game.entities.remove(self)

class Projectile(Entity):
    def __init__(self, game, pos, direction, owner, speed=8, sprite=None,damage=1):
        self.owner = owner
        self.direction = direction
        self.speed = speed
        self.damage = damage

        if sprite is None:
            if owner == 'player':
                sprite = game.assets['tear_sheet']
            else:
                sprite = game.assets['blood_tear_sheet']

        scale = 2
        w, h = sprite.get_width(), sprite.get_height()
        sprite = pygame.transform.scale(sprite, (w*scale, h*scale))
        
        # HITBOX ŁZY 
        # 20x20 wyśrodkowany
        hb_w, hb_h = 20, 20
        off_x = (w - hb_w) // 2 + 33
        off_y = (h - hb_h) // 2 + 30

        super().__init__(game, 'projectile', pos, 
                         sprite.get_size(), 
                         sprite, 
                         hitbox_size=(hb_w, hb_h),
                         hitbox_offset=(off_x, off_y))

        self.mask = pygame.mask.from_surface(sprite)

    def update(self, dt=0):
        self.pos[0] += self.direction[0] * self.speed
        self.pos[1] += self.direction[1] * self.speed
        
        # synchronizacja hitboxa z nową pozycją
        self.sync_hitbox_to_pos()

        # Kolizja ze ścianą
        if self.hitbox.left < config.GRID_BORDER_LEFT or self.hitbox.right > config.GRID_BORDER_RIGHT or \
           self.hitbox.top < config.GRID_BORDER_TOP or self.hitbox.bottom > config.GRID_BORDER_BOTTOM:
               if self in self.game.entities:
                   self.game.entities.remove(self)
               return

        self.check_collisions()

    def check_collisions(self):
        for entity in self.game.entities[:]:
            if entity is self:
                continue

            if self.owner == "player" and entity.type != "enemy":
                continue
            if self.owner == "enemy" and entity.type != "player":
                continue

            # Hitbox vs Hitbox
            if not self.hitbox.colliderect(entity.hitbox):
                continue
            

            if entity.type == "enemy" and self.owner == "player":
                entity.on_collsion_enemy(self)
            elif entity.type == "player" and self.owner == "enemy":
                entity.on_collsion_enemy(self)

            # Usuwamy pocisk po trafieniu
            if self in self.game.entities:
                self.game.entities.remove(self)
            return

class Pickup(Entity):
    def __init__(self, game, pos):
        raw_img = game.ui.heart 
        img = pygame.transform.scale(raw_img, (32, 32)) 
        super().__init__(game, "pickup", pos, img.get_size(), img, hitbox_size=(24, 24))
        self.solid = False

    def on_pickup(self, player):
        if player.hp < player.max_hp:
            player.hp += 1
            if self in self.game.entities:
                self.game.entities.remove(self)

class Trapdoor(Entity):
    def __init__(self, game, pos):
        size_px = (config.TILE_WIDTH * 3, config.TILE_HEIGHT * 3)
        raw_img = game.assets.get('trapdoor')
        
        if raw_img:
            img = pygame.transform.scale(raw_img, size_px)
        else:
            img = pygame.Surface(size_px)
            img.fill((50, 50, 50))
            pygame.draw.rect(img, (0,0,0), img.get_rect(), 5)
        
        top_left = (pos[0] - size_px[0]//2, pos[1] - size_px[1]//2)
        
        super().__init__(game, "trapdoor", top_left, size_px, img, hitbox_size=(80, 80))
        self.solid = False
    
    def on_enter(self, player):
        self.game.next_level()