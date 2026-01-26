import pygame
import Entities
from Utils import load_image, EventHandlingMoj , spawn_enemy
from mobs import get_mobs_config, get_player_config
from UIMoj import UI
WIDTH, HEIGHT = 1280, 720
FPS = 60
FRAME_W = 32
FRAME_H = 32

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        pygame.display.set_caption("The Binding of Isaac: Derpentance ")
        self.movement = [False, False, False, False]#right,left,up,down
        self.shooting = [False, False, False, False]#right,left,up,down
        self.assets = {
            'player_sheet':load_image('isaac/character_isaac.png'),
            'zombie_head_sheet':load_image('enemies/zombie_head.png'),
            'zombie_legs_sheet':load_image('enemies/zombie_legs.png'),
            'fly':load_image('enemies/fly.png'),
            'tear_sheet':load_image('tears/tear.png'),
            'blood_tear_sheet':load_image('tears/bloodtear.png'),
            'heart_sheet':load_image('ui/hearts.png'),
        }
        self.isaac_animations = get_player_config(self.assets)
        self.enemies_animations = get_mobs_config(self.assets)


        self.player = Entities.Player(self, (50, 50))
        self.entities = [self.player]
        spawn_enemy(self, "zombie", (200, 200))

        spawn_enemy(self, "zombie", (500, 500))
        spawn_enemy(self, "fly", (600, 500))
        self.ui = UI(self)
    def run(self):
        while True:
            self.screen.fill((255, 255, 255))

            dt = self.clock.tick(FPS)

            EventHandlingMoj(self.movement, self.shooting)

            for e in self.entities[:]:
                if isinstance(e, Entities.Enemy):
                    e.update(dt)
                else:
                    e.update()
                if not isinstance(e, Entities.Player):
                     e.render(self.screen)

            self.player.update(self.movement, self.shooting,dt)
            self.player.render(self.screen)
            self.ui.render(self.screen)
            if self.player.hp <=0:
                print("Game Over")
            pygame.display.update()
            self.clock.tick(FPS)

Game().run()