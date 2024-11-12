from board import Direction, Rotation, Action
from random import Random
import time

class Player:
    def choose_action(self, board):
        moves = get_possible_moves(board)
        if not moves:
            return None 
        best_move = choose_best_move(moves)
        
        actions = []

        if best_move['rotation'] is not None:
            actions.append(best_move['rotation'])
        if best_move['translation'] < 0:
            actions.extend([Direction.Left] * -best_move['translation'])
        elif best_move['translation'] > 0:
            actions.extend([Direction.Right] * best_move['translation'])
        actions.append(Direction.Drop)
        
        return actions

""" TO DO: Crear una función que me devuelva la mejor acción no solo teniendo en cuenta
completar una linea, si no puntuando más que las lineas se completen de 4 en 4.

"""

def get_possible_moves(board):
    moves = []
    rotations = [None, Rotation.Clockwise, Rotation.Anticlockwise] 
    for rotation in rotations:
        for translation in range(-board.width + 1, board.width):
            sandbox = board.clone()
            if rotation is not None:
                sandbox.rotate(rotation)
            if translation < 0:
                for _ in range(-translation):
                    sandbox.move(Direction.Left)
            elif translation > 0:
                for _ in range(translation):
                    sandbox.move(Direction.Right)
            landed = sandbox.move(Direction.Drop)
            if not is_valid_position(sandbox):
                continue
            score = evaluate_board(sandbox)
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
    
    score = (-0.6 * max_height) + (-0.7 * holes) + (1.0 * complete_lines) + (-0.3 * bumpiness)
    return score

def get_column_heights(board):
    heights = [0] * board.width
    for x in range(board.width):
        column_cells = [y for (cx, y) in board.cells if cx == x]
        if column_cells:
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
    if board.falling is None:
        return True
    for (x, y) in board.falling.cells:
        if x < 0 or x >= board.width or y < 0 or y >= board.height:
            return False
        if (x, y) in board.cells:
            return False
    return True

SelectedPlayer = Player
