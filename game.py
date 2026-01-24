import pygame # wczytanie modułu pygame
import config
from main_menu import MainMenu
from state_machine import StateMachine

pygame.init() # inicjalizacja modułu pygame

# Stworzenie okienka
window_surface = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

# Inicjalizacja obiektów gry
manager = StateMachine()
main_menu = MainMenu(manager)

""" 
============================
TYMCZASOWE OKNO GRY
"""
def draw_placeholder(surface):
    surface.fill((50, 0, 0))
    text = font.render('TU BĘDZIE GRA KIEDYŚ', True, config.COLOR_WHITE)
    surface.blit(text, (300, 300))
"""
============================
"""

# Stworzenie czcionek
font = pygame.font.Font(config.FONT_PATH, config.FONT_SIZE)
font_large = pygame.font.Font(config.FONT_PATH, config.FONT_SIZE_LARGE)

# Nadanie nazwy okienka
pygame.display.set_caption('The Skibidi of Paweł: Rebirth')

# Utworzenie zegara pilnującego klatki na sekundę
clock = pygame.time.Clock()

# Stworzenie zmiennej, która określa, czy gra powinna być otwarta
game_status = True

while game_status:
    # Wczytanie wszystkich zdarzeń
    events = pygame.event.get()

    # Rozpatrzenie każdego ze zdarzeń
    for event in events:
        # Wyświetlenie zdarzenia w konsoli
        #print(event)

        # Jeżeli typ zdarzenia to zamknięcie gry
        if event.type == pygame.QUIT:
            # To zmieniamy status gry na nieaktywną
            game_status = False

    # Logika stanu
    current_state = manager.get_state()

    if current_state == 'menu':
        main_menu.update(events)
        main_menu.draw(window_surface, font, font_large)
    elif current_state == 'game':
        draw_placeholder(window_surface)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            manager.set_state('menu')

    # Odświeżanie okna
    pygame.display.update()
    
    # Obliczenie ile czasu zajmie jedna klatka
    clock.tick(60)
    pass

# Zamknięcie aplikacji
#pygame.quit()
#quit()
main_menu.quit_game()