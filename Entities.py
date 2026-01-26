import pygame
from mobs import get_mobs_stats

class Entity:
    def __init__(self, game, e_type, pos, size, sprite=None):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.sprite = sprite
        self.hitbox = pygame.Rect(self.pos[0], self.pos[1], size[0], size[1])
        self.mask = None
        if self.sprite:
            self.mask = pygame.mask.from_surface(self.sprite)
        self.solid = False

    def update(self, movement=(0, 0)):

        self.pos[0] += movement[0] + self.velocity[0]
        self.hitbox.topleft = self.pos
        if self.check_solid_collision():
            self.pos[0] -= movement[0] + self.velocity[0]
            self.hitbox.topleft = self.pos

        self.pos[1] += movement[1] + self.velocity[1]
        self.hitbox.topleft = self.pos
        if self.check_solid_collision():
            self.pos[1] -= movement[1] + self.velocity[1]
            self.hitbox.topleft = self.pos


        self.check_damage_collision()

    def render(self, surf):
        if self.sprite:
            surf.blit(self.sprite, self.pos)


    def check_solid_collision(self):
        for entity in self.game.entities:
            if entity is self or not getattr(entity, "solid", False):
                continue
            if self.hitbox.colliderect(entity.hitbox):
                return True
        return False


    def check_damage_collision(self):
        for entity in self.game.entities:
            if entity is self:
                continue
            if not self.hitbox.colliderect(entity.hitbox):
                continue
            if self.mask and entity.mask:
                offset = (entity.hitbox.x - self.hitbox.x,
                          entity.hitbox.y - self.hitbox.y)
                if self.mask.overlap(entity.mask, offset):

                    if self.type == 'player' and entity.type == 'enemy':
                        self.on_collsion_enemy(entity)

                    elif self.type == 'enemy' and entity.type == 'player':
                        entity.on_collsion_enemy(self)

    def on_collsion_enemy(self, enemy):

        if not hasattr(self, 'invincible'):
            self.hp -= enemy.damage
            if self.hp <= 0 and self in self.game.entities:
                self.game.entities.remove(self)
            return


        if self.invincible:
            return

        self.hp -= enemy.damage
        self.invincible = True
        self.last_hit_time = pygame.time.get_ticks()

        if self.hp <= 0 and self in self.game.entities:
            self.game.entities.remove(self)


class Player(Entity):
    def __init__(self, game, pos, scale=3):
        stats = get_mobs_stats()['player']
        self.hp = stats["hp"]
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
                        pygame.transform.scale(frame,
                                               (frame.get_width() * scale, frame.get_height() * scale)
                                               ) for frame in sprite
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
                        pygame.transform.scale(frame,
                                               (frame.get_width() * scale, frame.get_height() * scale)
                                               ) for frame in sprite
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

        super().__init__(game, 'player', pos, (head_idle.get_width(), head_idle.get_height()), head_idle)

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
        if shooting[0]: return (1, 0)  # right
        if shooting[1]: return (-1, 0)  # left
        if shooting[2]: return (0, -1)  # up
        if shooting[3]: return (0, 1)  # down
        return None

    def shoot(self, direction):

        bullet_pos = (
            self.pos[0] + self.size[0] // 2 - self.tear_sprite.get_width() // 2  -35,
            self.pos[1] + self.size[1] // 4 - self.tear_sprite.get_height() // 2 +15
        )

        bullet = Projectile(
            self.game,
            bullet_pos,
            direction,
            damage=self.damage,
            owner='player',
            sprite=self.tear_sprite
        )

        self.game.entities.append(bullet)

    def die(self):
        print("Player dead")


    def render(self, surf):

        body_frames = self.body_animations[self.body_facing]
        if self.body_state == 'walking' and 'walking' in body_frames:
            frames = body_frames['walking']
            frame = frames[self.legs_index % len(frames)]
        else:
            frame = body_frames['idle']


        body_pos = (self.pos[0], self.pos[1] + self.head_animations[self.head_facing][self.head_state].get_height()//2 -10)
        surf.blit(frame, body_pos)


        head_frame = self.head_animations[self.head_facing][self.head_state]
        if isinstance(head_frame, list):
            head_frame = head_frame[0]
        surf.blit(head_frame, self.pos)



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

        super().__init__(game, "enemy", pos, (total_width, total_height), self.head_sprite)
        self.mask = pygame.mask.from_surface(self.head_sprite)


        self.last_shot = 0

    def update(self, dt=0):
        player = self.game.player
        if not player:
            return

        dx = player.hitbox.centerx - self.hitbox.centerx
        dy = player.hitbox.centery - self.hitbox.centery
        mag = (dx ** 2 + dy ** 2) ** 0.5
        if mag != 0:
            dx /= mag
            dy /= mag

        next_pos = [self.pos[0] + dx * self.speed, self.pos[1] + dy * self.speed]
        next_hitbox = self.hitbox.copy()
        next_hitbox.topleft = next_pos




        self.pos = next_pos
        self.hitbox.topleft = self.pos

        self.check_damage_collision()

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
            self.pos[0] + self.head_sprite.get_width() // 2 - self.tear_sprite.get_width() // 2 -35,
            self.pos[1] + self.head_sprite.get_height() // 2 - self.tear_sprite.get_height() // 2
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
        size = (w*scale, h*scale)

        super().__init__(game, 'projectile', pos, sprite.get_size(), sprite)
        self.mask = pygame.mask.from_surface(sprite)

    def update(self, dt=0):
        self.pos[0] += self.direction[0] * self.speed
        self.pos[1] += self.direction[1] * self.speed
        self.hitbox.topleft = self.pos

        self.check_collisions()

    def render(self, surf):
        if self.sprite:
            surf.blit(self.sprite, self.pos)

    def check_collisions(self):
        for entity in self.game.entities[:]:
            if entity is self:
                continue

            if self.owner == "player" and entity.type != "enemy":
                continue
            if self.owner == "enemy" and entity.type != "player":
                continue

            if not self.hitbox.colliderect(entity.hitbox):
                continue

            if self.mask and entity.mask:
                offset = (entity.hitbox.x - self.hitbox.x,
                          entity.hitbox.y - self.hitbox.y)
                if self.mask.overlap(entity.mask, offset):
                    if entity.type == "enemy" and self.owner == "player":
                        entity.on_collsion_enemy(self)
                    elif entity.type == "player" and self.owner == "enemy":
                        entity.on_collsion_enemy(self)

                    if self in self.game.entities:
                        self.game.entities.remove(self)
                    return
