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

        for heights in get_column_heights(board):
            if heights > 16 and board.bombs_remaining > 0:
                actions.append(Action.Bomb)
                actions.append(Direction.Drop)
        if best_move['rotation'] is not None:
            if board.falling is not None:
                actions.append(best_move['rotation'])
        if best_move['rotation'] is not None:
            if board.falling is not None:
                actions.append(best_move['rotation2'])
        if best_move['translation'] < 0:
            if board.falling is not None:   
                actions.extend([Direction.Left] * -best_move['translation'])
        elif best_move['translation'] > 0:
            if board.falling is not None:
                actions.extend([Direction.Right] * best_move['translation'])
        if board.falling is not None:
            actions.append(Direction.Drop)
        
        return actions


def get_possible_moves(board):
    if board.falling is None:
        return []
    
    #TO DO TAKE INTO ACCOUNT ALL THE POSSIBLE ROTATIONS
    #QUE TARDE MENOS
    moves = []
    rotations = [Rotation.Clockwise, Rotation.Anticlockwise]
    rotations2 = [None, Rotation.Clockwise, Rotation.Anticlockwise] 

    for rotation in rotations:
        for rotation2 in rotations2:
            for translation in range(-board.width + 1, board.width):
               sandbox = board.clone()
               if sandbox.falling is None:
                  continue
               if rotation is not None:
                    if sandbox.falling is not None:
                      if board.falling is not None:
                           sandbox.rotate(rotation)
               if rotation2 is not None:
                    if sandbox.falling is not None:
                        sandbox.rotate(rotation2)
               if translation < 0:
                    for _ in range(-translation):
                        if sandbox.falling is not None:
                            if board.falling is not None:
                                sandbox.move(Direction.Left)
               elif translation > 0:
                    for _ in range(translation):
                        if sandbox.falling is not None:
                            if board.falling is not None:
                                sandbox.move(Direction.Right)
               if sandbox.falling is not None:
                    if board.falling is not None:
                        sandbox.move(Direction.Drop)
               old_cells = len(board.cells)


               if not is_valid_position(sandbox):
                    continue
               
               #moves2 = get_possible_moves2(board)
               #best_move2 = choose_best_move(moves2)
               #score2 = best_move2['score']
               score = evaluate_board(sandbox, board)# + score2
               moves.append({
                    'rotation': rotation,
                    'translation': translation,
                    'score': score,
                    'rotation2': rotation2   
                })
    return moves
"""
def get_possible_moves2(board):
    if board.falling is None:
        return []

    moves2 = []
    rotations = [Rotation.Clockwise, Rotation.Anticlockwise] 
    rotations2 = [None, Rotation.Clockwise, Rotation.Anticlockwise]

    for rotation in rotations:
        for rotation2 in rotations2:
            for translation in range(-board.width + 1, board.width):
                
                sandbox = board.clone()
                if sandbox.falling is None:
                    continue  # Skip if clone does not have a falling block
                if rotation is not None:
                    if sandbox.falling is not None:
                        sandbox.rotate(rotation)
                if rotation is not None:
                    if sandbox.falling is not None:
                        sandbox.rotate(rotation2)
                if translation < 0:
                    for _ in range(-translation):
                        if sandbox.falling is not None:
                            sandbox.move(Direction.Left)
                elif translation > 0:
                    for _ in range(translation):
                        if sandbox.falling is not None:
                                sandbox.move(Direction.Right)
                if sandbox.falling is not None:
                        sandbox.move(Direction.Drop)

                if not is_valid_position(sandbox):
                    continue

                score = evaluate_board(sandbox, old_cells)
                moves2.append({
                    'rotation': rotation,
                    'translation': translation,
                    'score': score,
                    'rotation2': rotation2
                })
    return moves2
"""

def choose_best_move(moves):
    best_move = max(moves, key=lambda x: x['score'])
    return best_move

def evaluate_board(board, old_board):
    new_cells = len(board.cells)
    linesmultiplier = 0
    heights = get_column_heights(board)
    max_height = max(heights)
    sum_heights = get_height_sum(board)
    holes = count_holes(board, heights)
    bumpiness = calculate_bumpiness(heights)

    score_difference = board.score - old_board.score

    if score_difference < 25:
        complete_lines = 0
    elif score_difference < 100:
        complete_lines = 1
    elif score_difference < 400:
        complete_lines = 2
    elif score_difference < 1600:
        complete_lines = 3
    else:
        complete_lines = 4
    if complete_lines != 0:
        print("complete lines: ", complete_lines)

    if complete_lines == 4:
        linesmultiplier = 100000000000000000000000
    if complete_lines == 3:
        linesmultiplier = 0.05
    if complete_lines == 2:
        linesmultiplier = -2.6
    if complete_lines == 1:
        linesmultiplier = -6.3
    if complete_lines == 3:
        linesmultiplier = 0
    
    #Not working Panic Zone
    #if max_height > 14:
     #   score = (-20 * sum_heights) + (1000 * complete_lines) + (-0.5 * holes) + (-0.2 * bumpiness) + (-13 * max_height)
    #else:
    #especific weight
    score = (-0.6 * sum_heights) + (linesmultiplier * complete_lines) + (-5.9 * holes) + (-0.534 * bumpiness)
    return score

"""AVERAGE 16k:
if complete_lines == 4:
        linesmultiplier = 100000000000000000
    if complete_lines == 3:
        linesmultiplier = 0.15
    if complete_lines == 2:
        linesmultiplier = -2.1
    if complete_lines == 1:
        linesmultiplier = -4.9
    if complete_lines == 3:
        linesmultiplier = 0
    
    #Not working Panic Zone
    if max_height > 14:
        score = (-20 * sum_heights) + (1000 * complete_lines) + (-0.5 * holes) + (-0.2 * bumpiness) + (-13 * max_height)
    else:
    #especific weight
        score = (-0.38 * sum_heights) + (linesmultiplier * complete_lines) + (-4.4 * holes) + (-0.384 * bumpiness)
    return score
"""
"""WEIGHTS THAT GAVE ME 24k ONCE (average 6k - 16k):

if complete_lines == 4:
        linesmultiplier = 100000000000000000
    if complete_lines == 3:
        linesmultiplier = 0.15
    if complete_lines == 2:
        linesmultiplier = -2.1
    if complete_lines == 1:
        linesmultiplier = -4.9
    if complete_lines == 3:
        linesmultiplier = 0
    
    #Not working Panic Zone
    if max_height > 14:
        score = (-20 * sum_heights) + (1000 * complete_lines) + (-0.5 * holes) + (-0.2 * bumpiness) + (-13 * max_height)
    else:
    #especific weight
        score = (-0.38 * sum_heights) + (linesmultiplier * complete_lines) + (-4.4 * holes) + (-0.284 * bumpiness)
    return score
    
    """

def get_column_heights(board):
    heights = [0] * board.width
    for x in range(board.width):
        column_cells = [y for (cx, y) in board.cells if cx == x]
        if column_cells:
            heights[x] = board.height - min(column_cells)
        else:
            heights[x] = 0
    return heights

def get_height_sum(board):
    heightsum = 0
    for x in range(board.width):
        column_cells = [y for (cx, y) in board.cells if cx == x]
        if column_cells:
            heightsum += board.height - min(column_cells)
    return heightsum

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

