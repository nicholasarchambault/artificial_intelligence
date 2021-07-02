from engines import Engine
from copy import deepcopy
import time

class StudentEngine(Engine):

    depth_max = 2
    alpha_beta = False

    # Metrics for statistical tests
    num_nodes = 0
    duplicates = 0

    leaves = 0

    runtime = 0
    total_iterations = 0

    archive = set()

    # Added commented lines to code in order to run certain tests to get statistics.
    # Did not modify main body of 'get_move()'
    
    def get_move(self, board, color, move_num=None,
                 time_remaining=None, time_opponent=None):

        # self.total_iterations += 1
        # begin = time.time()

        f = self.get_ab_minimax_move if self.alpha_beta else self.get_minimax_move
        move = f(board, color, move_num, time_remaining, time_opponent)
        
        # self.runtime += (time.time() - begin)
        
        # self.summary_stats()
        return move

    def get_minimax_move(self, board, color, move_num=None,
                         time_remaining=None, time_opponent=None):

        moves = board.get_legal_moves(color)        

        return max(moves, key=lambda move: self.minimax_score(board, move, color, color, 1))

    def minimax_score(self, board, move, start_color, current_color, depth):
        # self.num_nodes += 1

        new_board = deepcopy(board)
        new_board.execute_move(move, current_color)

        # self.get_duplicates(board, current_color)

        opponent_moves = new_board.get_legal_moves(-current_color)
        if depth == self.depth_max or len(opponent_moves) == 0:
            # self.leaves += 1
            return self.minimax_function(new_board, start_color)

        if start_color == current_color:
            best_score = float('-inf')
        else:
            best_score = float('inf')

        for i in opponent_moves:
            score = self.minimax_score(new_board, i, start_color, -current_color, depth + 1)
            if (start_color == current_color and score > best_score) or (start_color != current_color and score < best_score):
                best_score = score

        return best_score

    def minimax_function(self, board, color):

        opponent_pieces = len(board.get_squares(-color))
        my_pieces = len(board.get_squares(color))

        opponent_moves = len(board.get_legal_moves(-color))
        my_moves = len(board.get_legal_moves(color))

        corners_list = [[0, 0], [0, 7], [7, 0], [7, 7]]
        
        opponent_corners = 0
        my_corners = 0
        
        for i in corners_list:
            if board[i[0]][i[1]] == -color:
                opponent_corners += 1
            elif board[i[0]][i[1]] == color:
                my_corners += 1

                
        # See README doc for attribution on heuristic 
        return (0.01 * (my_pieces - opponent_pieces)  + 
                (my_moves - opponent_moves) + 
                10 * (my_corners - opponent_corners))


    def get_ab_minimax_move(self, board, color, move_num=None,
                            time_remaining=None, time_opponent=None):

        moves = board.get_legal_moves(color)

        return max(moves, key=lambda move: self.alpha_beta_move(board, move, color, color, 1, float('-inf'), float('inf')))

    def alpha_beta_move(self, board, move, start_color, current_color, depth, alpha, beta):
        # self.num_nodes += 1

        new_board = deepcopy(board)
        new_board.execute_move(move, current_color)

        # self.get_duplicates(board, current_color)

        opponent_moves = new_board.get_legal_moves(-current_color)
        if depth == self.depth_max or len(opponent_moves) == 0:
            # self.leaves += 1
            return self.minimax_function(new_board, start_color)

        if start_color == current_color:
            best_score = float('-inf')
        else:
            best_score = float('inf')

        for i in opponent_moves:
            score = self.alpha_beta_move(new_board, i, start_color, -current_color, depth + 1, alpha, beta)

            if start_color == current_color:
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
            else:
                best_score = min(best_score, score)
                beta = min(beta, best_score)
            if alpha >= beta:
                break

        return best_score

# Function for evaluating duplicate states
    def get_duplicates(self, board, current_color):
        title = ''
        for i in range(8):
            for j in range(8):
                title += str(board[i][j])
        title += str(current_color)

        if title not in self.archive:
            self.duplicates = self.duplicates + 1
        else:
            self.duplicates = self.duplicates
        self.archive.add(title)

# Function for getting summary stats        

   # def summary_stats(self):
       # print(f'total nodes = { self.num_nodes }')
       # print(f'total duplicates = { self.duplicates }')
       # print(f'avg. branching factor per iteration = { self.num_nodes / (self.num_nodes - self.leaves) }')
       # print(f'runtime per iteration = { self.runtime / self.total_iterations }')

engine = StudentEngine
