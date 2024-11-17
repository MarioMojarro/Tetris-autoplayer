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
        if best_move['score'] < -60 and board.discards_remaining > 0:
            actions.append(Action.Discard)
        if best_move['rotation'] is not None:
            if board.falling is not None:
                actions.append(best_move['rotation'])
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
    
    moves = []
    moves2= []
    rotations = [None, Rotation.Clockwise, Rotation.Anticlockwise, Rotation.Clockwise.Clockwise] 
    #rotations2 = [None, Rotation.Clockwise]

    print(str(board.falling))

    for rotation in rotations:
            for translation in range(-board.width + 1, board.width):
               sandbox = board.clone()
               if sandbox.falling is None:
                  continue  # Skip if clone does not have a falling block
               if rotation is not None:
                    if sandbox.falling is not None:
                       if board.falling is not None:
                            sandbox.rotate(rotation)
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

               if not is_valid_position(sandbox):
                    continue
               
               #moves2 = get_possible_moves2(board)
               #best_move2 = choose_best_move(moves2)
               #score2 = best_move2['score']
               score = evaluate_board(sandbox)# + score2
               moves.append({
                    'rotation': rotation,
                    'translation': translation,
                    'score': score
                })
    return moves

def get_possible_moves2(board):
    if board.falling is None:
        return []
    
    moves2 = []
    rotations = [None, Rotation.Clockwise, Rotation.Anticlockwise, Rotation.Clockwise.Clockwise] 
    #rotations2 = [None, Rotation.Clockwise]

    print(str(board.falling))

    for rotation in rotations:
            for translation in range(-board.width + 1, board.width):
               
               sandbox = board.clone()
               if sandbox.falling is None:
                  continue  # Skip if clone does not have a falling block
               if rotation is not None:
                    if sandbox.falling is not None:
                       if board.next.falling is not None:
                            sandbox.rotate(rotation)
               if translation < 0:
                    for _ in range(-translation):
                        if sandbox.falling is not None:
                            if board.next.falling is not None:
                                sandbox.move(Direction.Left)
               elif translation > 0:
                    for _ in range(translation):
                        if sandbox.falling is not None:
                            if board.next.falling is not None:
                                sandbox.move(Direction.Right)
               if sandbox.falling is not None:
                    if board.next.falling is not None:
                        sandbox.move(Direction.Drop)

               if not is_valid_position(sandbox):
                    continue

               score = evaluate_board(sandbox)
               moves2.append({
                    'rotation': rotation,
                    'translation': translation,
                    'score': score
                })
    return moves2

def choose_best_move(moves):
    best_move = max(moves, key=lambda x: x['score'])
    return best_move

def evaluate_board(board):
    heights = get_column_heights(board)
    max_height = max(heights)
    sum_heights = get_height_sum(board)
    holes = count_holes(board, heights)
    complete_lines = count_complete_lines(board)
    two_lines = can_complete_two_lines(board)
    three_lines = can_complete_three_lines(board)
    four_lines = can_complete_four_lines(board)
    bumpiness = calculate_bumpiness(heights)
    
   

   #old weights
    #score = (-0.5 * max_height) + (-0.7 * holes) + (3 * complete_lines) + (-0.2 * bumpiness)
    if max_height > 18:
        score = (-1.5 * sum_heights) + (-1.5 * max_height) + (100 * complete_lines) + ( 150 * two_lines) + ( 200 * three_lines) + (1000 * four_lines)
    else:
    #especific weight
        #score = (-0.510066 * sum_heights) + (0.760667 * complete_lines) + (-0.35663 * holes) + (-0.184483 * bumpiness)
        score = (-0.510066 * sum_heights) + (-0.51 * complete_lines) + (-0.26 * two_lines) + (0.760667 * three_lines) + (10 * four_lines) + (-0.35663 * holes) + (-0.184483 * bumpiness)
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

def get_height_sum(board):
    heightsum = 0
    for x in range(board.width):
        column_cells = [y for (cx, y) in board.cells if cx == x]
        if column_cells:
            heightsum += board.height - min(column_cells)
            print("heightsum: " + str(heightsum))
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

def count_complete_lines(board):
    lines = 0
    for y in range(board.height):
        if all((x, y) in board.cells for x in range(board.width)):
            lines += 1
    return lines

def can_complete_two_lines(board):
    completed_lines = []
    for y in range(board.height):
        if all((x, y) in board.cells for x in range(board.width)):
            completed_lines.append(y)
    return len(completed_lines) == 2

def can_complete_three_lines(board):
    completed_lines = []
    for y in range(board.height):
        if all((x, y) in board.cells for x in range(board.width)):
            completed_lines.append(y)
    return len(completed_lines) == 3

def can_complete_four_lines(board):
    completed_lines = []
    for y in range(board.height):
        if all((x, y) in board.cells for x in range(board.width)):
            completed_lines.append(y)
    return len(completed_lines) == 4

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

