from board import Direction, Rotation, Action
from random import Random
import time

class Player2:
    def choose_action(self, board):
        raise NotImplementedError
    
class RandomPlayer(Player2):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x,y) in board.cells:
                    s += "#"
                else:
                    s += "."
            print(s, y)

    def choose_action(self, board):
        self.print_board(board)
        time.sleep(2)
        if self.random.random() > 0.97:
            # 3% chance we'll discard or drop a bomb
            return self.random.choice([
                Action.Discard,
                Action.Bomb,
            ])
        else:
            # 97% chance we'll make a normal move
            return self.random.choice([
                Direction.Left,
                Direction.Right,
                Direction.Down,
                Rotation.Anticlockwise,
                Rotation.Clockwise,
            ])

class Player:
    def choose_action(self, board):
        moves = get_possible_moves(board)
        if not moves:
            return None  # Si no hay movimientos, se salta el turno
        best_move = choose_best_move(moves)
        
        actions = []

        # Añadir rotación si es necesaria
        if best_move['rotation'] is not None:
            actions.append(best_move['rotation'])
        # Añadir movimientos horizontales
        if best_move['translation'] < 0: # Mover a la izquierda
            actions.extend([Direction.Left] * -best_move['translation'])
        elif best_move['translation'] > 0: # Mover a la derecha
            actions.extend([Direction.Right] * best_move['translation'])
        # Soltar el bloque
        actions.append(Direction.Drop)
        
        return actions

""" TO DO: Crear una función que me devuelva la mejor acción no solo teniendo en cuenta
completar una linea, si no puntuando más que las lineas se completen de 4 en 4.

"""

def get_possible_moves(board):
    moves = []
    rotations = [None, Rotation.Clockwise, Rotation.Anticlockwise]  # Eliminamos Rotation.Flipped
    for rotation in rotations:
        for translation in range(-board.width + 1, board.width):
            sandbox = board.clone()
            # Aplicar rotación si es necesaria
            if rotation is not None:
                sandbox.rotate(rotation)
            # Mover horizontalmente
            if translation < 0:
                for _ in range(-translation):
                    sandbox.move(Direction.Left)
            elif translation > 0:
                for _ in range(translation):
                    sandbox.move(Direction.Right)
            # Soltar el bloque
            landed = sandbox.move(Direction.Drop)
            # Verificar si el movimiento es válido
            if not is_valid_position(sandbox):
                continue
            # Evaluar el tablero resultante
            score = evaluate_board(sandbox)
            # Almacenar movimientos y puntaje
            moves.append({
                'rotation': rotation,
                'translation': translation,
                'score': score
            })
    return moves

def choose_best_move(moves):
    best_move = max(moves, key=lambda x: x['score'])
    return best_move

def evaluate_board(board):
    heights = get_column_heights(board)
    max_height = max(heights)
    holes = count_holes(board, heights)
    complete_lines = count_complete_lines(board)
    bumpiness = calculate_bumpiness(heights)
    
    # Pesos para la función de evaluación
    score = (-0.5 * max_height) + (-0.7 * holes) + (1.0 * complete_lines) + (-0.2 * bumpiness)
    return score

def get_column_heights(board):
    heights = [0] * board.width
    for x in range(board.width):
        column_cells = [y for (cx, y) in board.cells if cx == x]
        if column_cells:
            # Como y aumenta hacia abajo, la altura es la diferencia desde la parte superior
            heights[x] = board.height - min(column_cells)
        else:
            heights[x] = 0
    return heights

def count_holes(board, heights):
    holes = 0
    for x in range(board.width):
        column_cells = [y for (cx, y) in board.cells if cx == x]
        if column_cells:
            top_y = min(column_cells)
            for y in range(top_y + 1, board.height):
                if (x, y) not in board.cells:
                    holes += 1
    return holes

def count_complete_lines(board):
    lines = 0
    for y in range(board.height):
        if all((x, y) in board.cells for x in range(board.width)):
            lines += 1
    return lines

def calculate_bumpiness(heights):
    bumpiness = sum(abs(heights[i] - heights[i+1]) for i in range(len(heights)-1))
    return bumpiness

def is_valid_position(board):
    # Verifica si alguna celda está fuera de los límites o colisiona con otras piezas
    if board.falling is None:
        return True
    for (x, y) in board.falling.cells:
        if x < 0 or x >= board.width or y < 0 or y >= board.height:
            return False
        if (x, y) in board.cells:
            return False
    return True

SelectedPlayer = Player
