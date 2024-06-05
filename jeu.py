import pygame
import random

# Initialisation de pygame
pygame.init()

# Dimensions de la fenêtre et de la carte
tile_size = 30
size = 20
width, height = size * tile_size, size * tile_size
interface_height = 100  # Hauteur supplémentaire pour l'interface

# Couleurs
PASSABLE_COLOR = (200, 200, 200)        # Gris clair pour les cases passables
PLAYER_COLOR = (0, 0, 255)              # Bleu pour le joueur
PLAYER_COLOR_LIGHT = (100, 100, 255)    # Bleu clair pour le joueur capable de bouger
ENEMY_COLOR = (255, 0, 0)               # Rouge pour les ennemis
ENEMY_COLOR_LIGHT = (255, 100, 100)     # Rouge clair pour les ennemis capables de bouger
SELECTED_COLOR = (0, 255, 0)            # Vert pour la sélection
OBJECTIVE_MAJOR_COLOR = (255, 255, 0)   # Jaune pour objectif majeur
OBJECTIVE_MINOR_COLOR = (255, 215, 0)   # Doré pour objectif mineur

# Classes pour les unités
class Unit:
    def __init__(self, x, y, color, attributes, symbol):
        self.x = x
        self.y = y
        self.color = color
        self.attributes = attributes
        self.organization = attributes['ORGA_MAX']
        self.selected = False
        self.symbol = symbol
        self.speed = attributes['SPEED']
        self.moved = False  # Indicateur de mouvement pour le tour

    def draw(self, screen, units):
        #affichage du carré
        rect = pygame.Rect(self.x * tile_size, self.y * tile_size, tile_size, tile_size)
        if not self.moved:
            color = PLAYER_COLOR_LIGHT if self.color == PLAYER_COLOR else ENEMY_COLOR_LIGHT
        else:
            color = self.color
        pygame.draw.rect(screen, color, rect)
        
        #affichage du rectangle de selection       
        if self.selected:
            pygame.draw.rect(screen, SELECTED_COLOR, rect, 3)

        #Affichage du/des symboles de type d'unité
        font = pygame.font.SysFont(None, 16) 
        symbols = self.get_symbols_on_same_tile(units)
        combined_text = font.render(symbols, True, (255, 255, 255))
        text_width = combined_text.get_width()
        text_x = self.x * tile_size + (tile_size - text_width) // 2
        screen.blit(combined_text, (text_x, self.y * tile_size + 5))
        

    def can_move(self, x, y, game_map, units):
        if 0 <= x < size and 0 <= y < size:
            if abs(self.x - x) <= self.speed and abs(self.y - y) <= self.speed:
                return True
        return False

    def move(self, x, y):
        self.x = x
        self.y = y
        self.moved = True  # Marquer l'unité comme ayant bougé

    def attack(self, target_unit, game_map, units):
        if self.can_move(target_unit.x,target_unit.y,game_map,units) is True:
            print(self,  target_unit)
            
            target_initial_x, target_initial_y = target_unit.x, target_unit.y
            
            dx = target_initial_x - self.x
            dy = target_initial_y - self.y
            new_x, new_y = target_initial_x + dx, target_initial_y + dy
            print(new_x, new_y)
            
            if 0 <= new_x < size and 0 <= new_y < size :
                target_unit.move(new_x, new_y)


    def get_symbols_on_same_tile(self, units):
        symbols = [u.symbol for u in units if u.x == self.x and u.y == self.y]
        return ' '.join(symbols)

class Garrison(Unit):
    def __init__(self, x, y, color):
        attributes = {
            'NAME':"Garnison",
            'STRENGTH_MAX': 1000,
            'ORGA_MAX': 40,
            'DAILY_ORGA': 0.6,
            'RANGE': 1,
            'ATTACK': 20,
            'RESISTANCE': 30,
            'SPEED': 1
        }
        symbol = "G"
        super().__init__(x, y, color, attributes, symbol)

class Infantry(Unit):
    def __init__(self, x, y, color):
        attributes = {
            'NAME':"Infanterie",
            'STRENGTH_MAX': 3000,
            'ORGA_MAX': 60,
            'DAILY_ORGA': 1,
            'RANGE': 1,
            'ATTACK': 50,
            'RESISTANCE': 100,
            'SPEED': 1
        }
        symbol = "I"
        super().__init__(x, y, color, attributes, symbol)

class Tank(Unit):
    def __init__(self, x, y, color):
        attributes = {
            'NAME':"Tanks",
            'STRENGTH_MAX': 500,
            'ORGA_MAX': 50,
            'DAILY_ORGA': 0.6,
            'RANGE': 3,
            'ATTACK': 300,
            'RESISTANCE': 300,
            'SPEED': 2
        }
        symbol = "T"
        super().__init__(x, y, color, attributes, symbol)

# Générer la carte
def generate_map(size):
    return [[1 for _ in range(size)] for _ in range(size)]

# Afficher la carte
def draw_map(screen, game_map, tile_size):
    for y in range(len(game_map)):
        for x in range(len(game_map[y])):
            color = PASSABLE_COLOR
            pygame.draw.rect(screen, color, (x * tile_size, y * tile_size, tile_size, tile_size))

# Générer des unités sur des cases passables uniquement
def generate_units(game_map, player_color, enemy_color):
    units = []
    center_x, center_y = size // 2, size // 2
    player_positions = [(center_x - 1, center_y), (center_x, center_y - 1), (center_x + 1, center_y), (center_x, center_y + 1), (center_x - 1, center_y - 1)]
    enemy_positions = [(center_x - 2, center_y + 2), (center_x + 2, center_y + 2), (center_x + 2, center_y - 2), (center_x - 2, center_y + 2), (center_x + 1, center_y + 1)]

    player_units = [Garrison(*player_positions[0], player_color), Garrison(*player_positions[1], player_color), Infantry(*player_positions[2], player_color), Infantry(*player_positions[3], player_color), Tank(*player_positions[4], player_color)]
    enemy_units = [Garrison(*enemy_positions[0], enemy_color), Garrison(*enemy_positions[1], enemy_color), Infantry(*enemy_positions[2], enemy_color), Infantry(*enemy_positions[3], enemy_color), Tank(*enemy_positions[4], enemy_color)]
    
    units.extend(player_units)
    units.extend(enemy_units)
    
    return units

# Ajouter des objectifs à la carte
def add_objectives(game_map):
    objectives = []
    center_x, center_y = size // 2, size // 2
    while True:
        x, y = random.randint(center_x - 2, center_x + 2), random.randint(center_y - 2, center_y + 2)
        if game_map[y][x] == 1 and not any(obj['x'] == x and obj['y'] == y for obj in objectives):
            objectives.append({'x': x, 'y': y, 'type': 'MAJOR'})
            break

    for _ in range(2):
        while True:
            x, y = random.randint(center_x - 4, center_x + 4), random.randint(center_y - 4, center_y + 4)
            if game_map[y][x] == 1 and not any(obj['x'] == x and obj['y'] == y for obj in objectives):
                objectives.append({'x': x, 'y': y, 'type': 'MINOR'})
                break

    return objectives

# Afficher les objectifs
def draw_objectives(screen, objectives, tile_size):
    for obj in objectives:
        color = OBJECTIVE_MAJOR_COLOR if obj['type'] == 'MAJOR' else OBJECTIVE_MINOR_COLOR
        pygame.draw.rect(screen, color, (obj['x'] * tile_size, obj['y'] * tile_size, tile_size, tile_size))

# Afficher le message de changement de tour
def draw_turn_indicator(screen, player_turn):
    font = pygame.font.SysFont(None, 36)
    text = "Joueur" if player_turn else "Ennemi"
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (10, 10))

# Afficher le bouton de changement de tour
def draw_end_turn_button(screen, width, height, interface_height):
    font = pygame.font.SysFont(None, 36)
    text = font.render("Terminé", True, (255, 255, 255))
    button_rect = pygame.Rect(width // 2 - 50, height, 100, interface_height - 10)
    pygame.draw.rect(screen, (100, 100, 100), button_rect)
    screen.blit(text, (width // 2 - 50 + 10, height + 10))

# Vérifier si le bouton de changement de tour est cliqué
def end_turn_button_clicked(mouse_pos, width, height, interface_height):
    x, y = mouse_pos
    button_rect = pygame.Rect(width // 2 - 50, height, 100, interface_height - 10)
    return button_rect.collidepoint(x, y)

# Afficher les attributs de l'unité sélectionnée
def draw_unit_attributes(screen, unit, width, height, interface_height):
    if unit:
        font = pygame.font.SysFont(None, 24)
        unit_text = f"Type: {unit.attributes['NAME']}"
        strength_text = f"Force: {unit.attributes['STRENGTH_MAX']}"
        orga_text = f"Organisation: {unit.organization} / {unit.attributes['ORGA_MAX']}"
        unit_img = font.render(unit_text, True, (255, 255, 255))
        strength_img = font.render(strength_text, True, (255, 255, 255))
        orga_img = font.render(orga_text, True, (255, 255, 255))
        screen.blit(unit_img, (10, height + 10))
        screen.blit(strength_img, (10, height + 40))
        screen.blit(orga_img, (10, height + 70))

# Configuration de la fenêtre
screen = pygame.display.set_mode((width, height + interface_height))
pygame.display.set_caption("Carte de 20x20 avec unités et déplacement")

# Générer une carte de 20 par 20
game_map = generate_map(size)

# Générer les unités
units = generate_units(game_map, PLAYER_COLOR, ENEMY_COLOR)

# Ajouter des objectifs
objectives = add_objectives(game_map)

selected_unit = None
player_turn = True  # True pour le tour du joueur, False pour le tour de l'ennemi
turn_counter = 0
units_to_move = [unit for unit in units if (unit.color == PLAYER_COLOR if player_turn else unit.color == ENEMY_COLOR)]

# Boucle principale du jeu
running = True
while running:
    unit_moved = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if end_turn_button_clicked((x, y), width, height, interface_height):
                unit_moved = True
            else:
                grid_x, grid_y = x // tile_size, y // tile_size
                if event.button == 1:  # Clic gauche pour sélectionner
                    possible_units = [u for u in units if u.x == grid_x and u.y == grid_y and not u.moved]
                    if selected_unit:
                        if possible_units:
                            current_index = possible_units.index(selected_unit)
                            selected_unit.selected = False
                            selected_unit = possible_units[(current_index + 1) % len(possible_units)]
                            selected_unit.selected = True
                    else:
                        if possible_units:
                            selected_unit = possible_units[0]
                            selected_unit.selected = True
                elif event.button == 3:  # Clic droit pour déplacer ou attaquer
                    if selected_unit:
                        target_unit = [u for u in units if u.x == grid_x and u.y == grid_y and u.color != selected_unit.color]
                        
                        for cible in target_unit:                                
                            selected_unit.attack(cible, game_map, units)
                            
                        if selected_unit.can_move(grid_x, grid_y, game_map, units):
                            selected_unit.move(grid_x, grid_y)
                            selected_unit.selected = False
                            selected_unit = None

    if unit_moved:
        for unit in units_to_move:
            unit.moved = False  # Réinitialiser l'indicateur de mouvement
        player_turn = not player_turn
        units_to_move = [unit for unit in units if (unit.color == PLAYER_COLOR if player_turn else unit.color == ENEMY_COLOR)]
        turn_counter += 1
        if turn_counter % 2 == 0:
            for unit in units:
                unit.organization = min(unit.organization + unit.attributes['DAILY_ORGA'], unit.attributes['ORGA_MAX'])
        
        pygame.display.flip()
        pygame.time.wait(2000)

    screen.fill((0, 0, 0))
    draw_map(screen, game_map, tile_size)
    draw_objectives(screen, objectives, tile_size)
    
    for unit in units:
        unit.draw(screen, units)

    draw_turn_indicator(screen, player_turn)
    draw_end_turn_button(screen, width, height, interface_height)
    draw_unit_attributes(screen, selected_unit, width, height, interface_height)
    
    pygame.display.flip()

pygame.quit()
