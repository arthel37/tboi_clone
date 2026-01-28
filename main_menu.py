import config
import pygame
import sys
from button import Button

class MainMenu:
    def __init__(self, manager, game_instance, vignette=None):
        print('Tworzenie obiektu menu...')
        self.manager = manager
        self.game = game_instance
        self.vignette = vignette
        
        mid_x = config.WINDOW_WIDTH // 2
        start_y = config.WINDOW_HEIGHT // 2.5

        button_width = config.WINDOW_WIDTH // 6
        button_height = config.WINDOW_HEIGHT // 10
        button_x_offset = config.WINDOW_WIDTH // 25
        button_x_pos = button_x_offset + mid_x - button_width // 2

        print('\tTworzenie przycisków...')
        self.buttons = [
            Button("New game", button_x_pos, start_y, button_width, button_height, self.start_game),
            Button("Continue", button_x_pos, start_y + button_height, button_width, button_height, self.continue_game),
            Button("Settings", button_x_pos, start_y + button_height * 2, button_width, button_height, self.open_settings),
            Button("Exit", button_x_pos, start_y + button_height * 3, button_width, button_height, self.quit_game)
        ]

        self.selected_button_idx = 0

        print('\tWczytywanie klatek animacji tła...')
        try:
            bckg_image_1 = pygame.image.load('data/images/menu/main_menu1.png').convert()
            bckg_image_2 = pygame.image.load('data/images/menu/main_menu2.png').convert()

            self.bckg_frames = [
                pygame.transform.scale(bckg_image_1, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)),
                pygame.transform.scale(bckg_image_2, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)),
            ]
        except FileNotFoundError:
            print(f'Nie odnaleziono obrazków tła')
            self.bckg_frames = []

        self.curr_bckg_idx = 0
        self.last_switch_time = 0
        print('\tZakończono tworzenie menu.')

    def start_game(self):
        print("Rozpoczynanie nowej gry")
        self.game.reset() 
        self.manager.set_state('game')

    def continue_game(self):
        print("Wznawianie gry")
        self.manager.set_state('game')

    def open_settings(self):
        print("Otwieranie ustawień")

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def update(self, events):
        curr_time = pygame.time.get_ticks()

        if curr_time - self.last_switch_time > 500:
            self.last_switch_time = curr_time
            self.curr_bckg_idx = (self.curr_bckg_idx + 1) % len(self.bckg_frames)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_button_idx += 1
                    if self.selected_button_idx >= len(self.buttons):
                        self.selected_button_idx = 0
                elif event.key == pygame.K_UP:
                    self.selected_button_idx -= 1
                    if self.selected_button_idx < 0:
                        self.selected_button_idx = len(self.buttons) - 1
                elif event.key == pygame.K_RETURN:
                    if self.buttons[self.selected_button_idx].action:
                        self.buttons[self.selected_button_idx].action()

    def draw(self, surface, font, font_large):
        if self.bckg_frames:
            curr_bckg = self.bckg_frames[self.curr_bckg_idx]
            surface.blit(curr_bckg, (0, 0))
        else:
            surface.fill((0, 0, 0))

        if self.vignette is not None:
            surface.blit(self.vignette, (0, 0))

        title_surf = font.render("The Binding of Isaac: Ripoff", True, config.COLOR_TEXT_DESELECT)
        title_rect = title_surf.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 10))
        surface.blit(title_surf, title_rect)

        for index, button in enumerate(self.buttons):
            is_selected = index == self.selected_button_idx
            button.draw(surface, is_selected, font, font_large)