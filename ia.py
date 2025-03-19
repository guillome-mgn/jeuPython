from constants import *

# IA
def ia(units, objectives, previous_actions):

    evaluate_player_intention(previous_actions)
   
    enemy_units = [unit for unit in units if unit.color == ENEMY_COLOR]
    player_units = [unit for unit in units if unit.color == PLAYER_COLOR]

    for unit in enemy_units:
        best_move = None
        best_score = -float('inf')

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                new_x, new_y = unit.x + dx, unit.y + dy

                if 0 <= new_x < size and 0 <= new_y < size:
                    if not any(u.x == new_x and u.y == new_y for u in units):
                        score = evaluate_position(new_x, new_y, unit, units, objectives)
                        if score == None:
                            best_move = None
                        elif score > best_score:
                            best_score = score
                            best_move = (new_x, new_y)

        # Effectuer le meilleur déplacement si trouvé
        if best_move:
            unit.move(*best_move)
            unit.moved = True  # Marquer l'unité comme ayant bougé
        elif best_move == None:
            # Ne pas se déplacer si aucun déplacement n'est le meilleur
            unit.moved = True
        
        # Évaluer les attaques possibles
        for target_unit in player_units:
            if unit.can_move(target_unit.x, target_unit.y):
                attack_score = evaluate_attack(unit, target_unit, units, objectives)
                if attack_score > best_score:
                    best_score = attack_score
                    unit.attack(target_unit, units, objectives)
                    unit.moved = True  # Marquer l'unité comme ayant attaqué
                    return  # Fin du tour de l'IA après avoir attaqué une unité
    # Si aucune unité n'a pu jouer, l'IA termine son tour
    player_turn = True

#Evalue la meilleur option de position pour l'ia
def evaluate_position(x, y, unit, units, objectives):

    # Si le pion est sur un objectif, il ne bouge pas
    for obj in objectives:
        if obj['x'] == unit.x and obj['y'] == unit.y:
            obj['enemyOnObjective'] = True
            return None
    
    score = 0
    distance_to_nearest_enemy = min(abs(unit.x - u.x) + abs(unit.y - u.y) for u in units if u.color != unit.color)
    # Calcule l'objectif le plus proche où aucun ennemi n'est présent
    do_all_objectives_have_enemies = all(obj['enemyOnObjective'] for obj in objectives)
    if do_all_objectives_have_enemies:
        distance_to_nearest_objective = min(abs(x - obj['x']) + abs(y - obj['y']) for obj in objectives if obj['type'] == 'MAJOR')
    else:
        distance_to_nearest_objective = min(abs(x - obj['x']) + abs(y - obj['y']) for obj in objectives if not obj['enemyOnObjective'])
    
    score -= distance_to_nearest_enemy  # Plus la distance est petite, mieux c'est
    score += 2 * (1 / (1 + distance_to_nearest_objective))  
    if any(obj['x'] == x and obj['y'] == y and obj['type'] == 'MAJOR' for obj in objectives):
        score += 5
    return score

def evaluate_attack(attacker, target, units, objectives):
    """Évalue la qualité d'une attaque de l'unité attaquante (attacker) sur l'unité cible (target)"""

    score = 0
    
    # Importance de la cible en fonction de sa santé restante (attaquer une unité faible est plus intéressant)
    # health_factor = 1 / (1 + target.pv)
    
    # Dommages potentiels de l'attaquant sur la cible
    # damage_potential = # attacker.attack_power
    
    # Influence sur les objectifs : Si l'unité cible est proche d'un objectif, l'attaque est plus importante
    distance_to_nearest_objective = min(abs(target.x - obj['x']) + abs(target.y - obj['y']) for obj in objectives)
    objective_factor = 2 * (1 / (1 + distance_to_nearest_objective))
    
    # Influence des unités environnantes : Si d'autres unités ennemies sont à proximité, cela peut améliorer le score
    nearby_enemies = [u for u in units if u.color == target.color and u != target]
    proximity_factor = sum(1 / (1 + abs(target.x - u.x) + abs(target.y - u.y)) for u in nearby_enemies)
    
    # Calcul du score final
    # score += health_factor * damage_potential  # Plus la santé de la cible est basse, plus l'attaque est précieuse
    score += objective_factor  # Plus la cible est proche d'un objectif, plus l'attaque est précieuse
    score += proximity_factor  # Plus il y a d'ennemis à proximité, plus l'attaque est précieuse
    
    return score

def evaluate_player_intention(previous_actions):
    """Évalue l'intention du joueur en fonction de ses actions précédentes"""
    for action in previous_actions:
        for unit in action.get_units():
            distances = evaluate_distance_from_objectives(unit, action.get_objectives())
            print(f"Distances de l'unité {unit} aux objectifs : {distances}")

def evaluate_distance_from_objectives(unit, objectives):
    """Évalue la distance entre une unité et tous les objectifs"""
    distances = []
    for obj in objectives:
        distance = abs(unit.x - obj['x']) + abs(unit.y - obj['y'])
        distances.append(distance)
    return distances