# This file is where game logic lives. No input
# or output happens here. The logic in this file
# should be unit-testable.
import numpy as np
from random import choice
from treelib import Tree, Node

cond_to_chr = {0: ' ', 1: 'O', 2: 'X'}
chr_to_int = {'a': 0, 'b': 1, 'c': 2}
int_to_role = {1: 'O', 2: 'X'}
role_to_int = {'O': 1, 'X': 2, None: 0}

def make_empty_board():
    return np.zeros([3,3])


class Game:
    def __init__(self, game_mode='pvp', start_first=True):
        self.board = make_empty_board()
        if game_mode == 'pvp':
            self.player_one = HumanPlayer(1)
            self.player_two = HumanPlayer(2)
        elif game_mode == 'pve':
            self.player_one = HumanPlayer(1)
            self.player_two = MinimaxBot(2)
        elif game_mode == 'eve':
            self.player_one = MinimaxBot(1)
            self.player_two = MinimaxBot(2)
        if start_first:
            self.player_now = self.player_one
        else:
            self.player_now = self.player_two

    def check_winner(self, player, board):
        checks = []
        checks += [all(board[0] == player), all(board[1] == player), all(board[2] == player)]
        checks += [all(board[:, 0] == player), all(board[:, 1] == player), all(board[:, 2] == player)]
        checks += [all(board.flatten()[0::4] == player), all(board.flatten()[2:7:2] == player)]
        return any(checks)


    def check_draw(self, board):
        return all(board.flatten() != 0)


    def get_winner(self, board):
        """Determines the winner of the given board.
        Returns 'X', 'O', or None."""
        if isinstance(board, list):
            board = np.array([[role_to_int[v] for v in l] for l in board])
        if self.check_winner(1, board):
            return 1
        elif self.check_winner(2, board):
            return 2
        else:
            return 0


    def other_player(self, player):
        """Given the character for a player, returns the other player."""
        return self.player_one if player == self.player_two else self.player_two


    def move(self, player, position):
        if position[0] is not None and position[1] is not None and position in player.get_available_moves(self.board):
            self.board[position[0]][position[1]] = player.player_id
            return True
        else:
            print("The place has already been taken!")
            return False
        
        
    def __repr__(self):
        separator = '---------------\n'
        header = '    0   1   2  \n'
        row_index='a'
        row_template = '%s | %s | %s | %s |\n'
        row_strings = []
        for i in range(3):
            row_strings.append(row_template % (chr(ord(row_index)+i), cond_to_chr[self.board[i][0]], cond_to_chr[self.board[i][1]], cond_to_chr[self.board[i][2]]))
        return header + separator.join(row_strings)
    
    
    def start(self):
        winner = None
        while winner == None:
            # TODO: Show the board to the user.
            print(self)
            # TODO: Input a move from the player.
            row, col = self.player_now.get_move(self)
            # TODO: Update the board.
            success = self.move(self.player_now, (row, col))
            # TODO: Update who's turn it is.
            if success:
                self.player_now = self.other_player(self.player_now)
            checked = self.get_winner(self.board)
            if checked != 0:
                winner = checked
                print(self)
                print("Player %s has won!!" % int_to_role[checked])
            if self.check_draw(self.board):
                print(self)
                print("Draw!")
                break
    


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
    
    
    def get_available_moves(self, board: np.ndarray):
        indices = np.where(board == 0)
        available = [(i, j) for i, j in zip(indices[0], indices[1])]
        return available

    def get_move(self, game):
        pass
    

class HumanPlayer(Player):
    def __init__(self, player_id):
        super().__init__(player_id)
    
    def get_move(self, game):
        try:
            position = input("Player %s please input the position you want to take, for example, \"a 0\"" % self.player_id)
            row, col = position.split()
            if row not in ['a', 'b', 'c']:
                print("Wrong input! The index of rows should be 'a', 'b', or 'c'")
                return None, None
            if col not in ['0', '1', '2']:
                print("Wrong input! The index of columns should be '0', '1', or '2'")
                return None, None
            row, col = chr_to_int[row], int(col)
            return row, col
        except Exception as e:
            print("Invalid input position command! Try again!")
            return None, None


class RandomBot(Player):
    def __init__(self, player_id):
        super().__init__(player_id)
        
    def get_move(self, game: Game):
        available = self.get_available_moves(game.board)
        return choice(available)
    
    
class MinimaxBot(Player):
    def __init__(self, player_id):
        super().__init__(player_id)
        
    def get_move(self, game: Game):
        if (game.board == 0).all():
            return 1, 1
        status_stack = ["root"]
        search_tree = Tree()
        search_tree.create_node("root", "root", data = {
            'board': np.copy(game.board),
            'turn': 'max',
            'move': None,
            'score': None,
            'depth': 0,
        })
        while len(status_stack) != 0:
            status_id = status_stack.pop()
            status_node = search_tree.get_node(status_id)
            status_board = status_node.data['board']
            availables = self.get_available_moves(status_board)
            for i, available in enumerate(availables):
                new_board = np.copy(status_board)
                new_board[available[0]][available[1]] = self.player_id if status_node.data['turn'] == 'max' else game.other_player(self).player_id
                new_board_data = {
                    'board': new_board,
                    'turn': 'min' if status_node.data['turn'] == 'max' else 'max',
                    'move': available,
                    'depth': status_node.data['depth'] + 1,
                }
                winner = game.get_winner(new_board)
                this_id = status_id + '-' + str(i)
                if winner != 0:
                    new_board_data['score'] = 10 - new_board_data['depth'] if winner == self.player_id else new_board_data['depth'] - 10
                elif game.check_draw(new_board):
                    new_board_data['score'] = 0
                else:
                    new_board_data['score'] = None
                    status_stack.append(this_id)
                search_tree.create_node(
                    this_id,
                    this_id,
                    parent=status_id,
                    data=new_board_data
                )
                
        all_nodes = search_tree.all_nodes()
        all_nodes.reverse()
        for node in all_nodes:
            assert isinstance(node, Node)
            if node.data['score'] is not None:
                continue
            else:
                children_nodes = search_tree.children(node.identifier)
                node.data['score'] = max([child.data['score'] for child in children_nodes]) if node.data['turn'] == 'max' else min([child.data['score'] for child in children_nodes])
        
        move = None
        max_score = -100
        for children in search_tree.children('root'):
            if children.data['score'] > max_score:
                max_score = children.data['score']
                move = children.data['move']
        return move
                
        
    
    
if __name__ == '__main__':
    game = Game(game_mode='pve', start_first=True)
    game.start()