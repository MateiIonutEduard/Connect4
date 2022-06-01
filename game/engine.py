import numpy as np
import random
import pygame
import sys
import math


class GameEngine(object):
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)

    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    rows = 6
    cols = 7

    PLAYER = 0
    AI = 1

    EMPTY = 0
    PLAYER_PIECE = 1

    AI_PIECE = 2
    WINDOW_LENGTH = 4
    BOX_SIZE = 100

    def __init__(self):
        self.board = np.zeros((self.rows, self.cols))
        self.game_over = False
        pygame.init()

        self.width = self.cols * self.BOX_SIZE
        self.height = (self.rows + 1) * self.BOX_SIZE
        self.size = (self.width, self.height)

        self.RADIUS = int(self.BOX_SIZE / 2 - 5)

        self.screen = pygame.display.set_mode(self.size)
        self.GamePaint(self.screen)
        pygame.display.update()

        self.font = pygame.font.SysFont("tahoma", 72)
        self.turn = random.randint(self.PLAYER, self.AI)
        pygame.display.set_caption("Connect 4")

    def GameUpdate(self):
        while not self.game_over:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(self.screen, self.BLACK, (0, 0, self.width, self.BOX_SIZE))
                    x_pos = event.pos[0]

                    if self.turn == self.PLAYER:
                        pygame.draw.circle(self.screen, self.RED, (x_pos, int(self.BOX_SIZE / 2)), self.RADIUS)

                pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(self.screen, self.BLACK, (0, 0, self.width, self.BOX_SIZE))

                    if self.turn == self.PLAYER:
                        x_pos = event.pos[0]
                        col = int(math.floor(x_pos / self.BOX_SIZE))

                        if self.board[self.rows - 1][col] == 0:
                            row = self.FindRow(self.board, col)
                            self.board[row][col] = self.PLAYER_PIECE

                            if self.PlayerWin(self.board, self.PLAYER_PIECE):
                                label = self.font.render("You win!!", 1, self.RED)
                                self.screen.blit(label, (40, 10))
                                game_over = True

                            self.turn += 1
                            self.turn = self.turn % 2
                            self.GamePaint(self.screen)

            if self.turn == self.AI and not self.game_over:

                col, minimax_score = self.AlphaBeta(self.board, 5, -math.inf, math.inf, True)

                if self.board[self.rows - 1][col] == 0:
                    row = self.FindRow(self.board, col)
                    self.board[row][col] = self.AI_PIECE

                    if self.PlayerWin(self.board, self.AI_PIECE):
                        label = self.font.render("Enemy wins!!", 1, self.YELLOW)
                        self.screen.blit(label, (40, 10))
                        self.game_over = True

                    self.GamePaint(self.screen)
                    self.turn += 1
                    self.turn = self.turn % 2

            if self.game_over:
                pygame.time.wait(3000)

    # Find next open row.
    def FindRow(self, table, w):
        for r in range(self.rows):
            if table[r][w] == 0:
                return r

    # Verify if player win this game !
    def PlayerWin(self, table, piece):
        for c in range(self.cols - 3):
            for r in range(self.rows):
                if table[r][c] == piece and table[r][c + 1] == piece and table[r][c + 2] == piece \
                        and table[r][c + 3] == piece:
                    return True

        for c in range(self.cols):
            for r in range(self.rows - 3):
                if table[r][c] == piece and table[r + 1][c] == piece and table[r + 2][c] == piece \
                        and table[r + 3][c] == piece:
                    return True

        for c in range(self.cols - 3):
            for r in range(self.rows - 3):
                if table[r][c] == piece and table[r + 1][c + 1] == piece and table[r + 2][c + 2] == piece \
                        and table[r + 3][c + 3] == piece:
                    return True

        for c in range(self.cols - 3):
            for r in range(3, self.rows):
                if table[r][c] == piece and table[r - 1][c + 1] == piece and table[r - 2][c + 2] == piece \
                        and table[r - 3][c + 3] == piece:
                    return True

    def Evaluate(self, window, piece):
        score = 0
        opp_piece = self.PLAYER_PIECE
        if piece == self.PLAYER_PIECE:
            opp_piece = self.AI_PIECE

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(self.EMPTY) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(self.EMPTY) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(self.EMPTY) == 1:
            score -= 4

        return score

    def score_position(self, table, piece):
        score = 0
        center_array = [int(i) for i in list(table[:, self.cols // 2])]

        center_count = center_array.count(piece)
        score += center_count * 3

        for r in range(self.rows):
            row_array = [int(i) for i in list(table[r, :])]

            for c in range(self.cols - 3):
                window = row_array[c:c + self.WINDOW_LENGTH]
                score += self.Evaluate(window, piece)

        for c in range(self.cols):
            col_array = [int(i) for i in list(table[:, c])]
            for r in range(self.rows - 3):
                window = col_array[r:r + self.WINDOW_LENGTH]
                score += self.Evaluate(window, piece)

        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                window = [table[r + i][c + i] for i in range(self.WINDOW_LENGTH)]
                score += self.Evaluate(window, piece)

        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                window = [table[r + 3 - i][c + i] for i in range(self.WINDOW_LENGTH)]
                score += self.Evaluate(window, piece)

        return score

    def IsLeafNode(self, table):
        return self.PlayerWin(table, self.PLAYER_PIECE) or self.PlayerWin(table, self.AI_PIECE) or len(self.GetMoves(table)) == 0

    def AlphaBeta(self, table, depth, alpha, beta, player):
        valid_locations = self.GetMoves(table)
        is_terminal = self.IsLeafNode(table)

        if depth == 0 or is_terminal:
            if is_terminal:
                if self.PlayerWin(table, self.AI_PIECE):
                    return None, 100000000000000
                elif self.PlayerWin(table, self.PLAYER_PIECE):
                    return None, -10000000000000
                else:
                    # Game is over ?!
                    return None, 0
            else:
                # Tree depth is 0.
                return None, self.score_position(table, self.AI_PIECE)

        if player:
            value = -math.inf
            column = random.choice(valid_locations)

            for w in valid_locations:
                h = self.FindRow(table, w)
                b_copy = table.copy()

                b_copy[h][w] = self.AI_PIECE
                new_score = self.AlphaBeta(b_copy, depth - 1, alpha, beta, False)[1]

                if new_score > value:
                    value = new_score
                    column = w

                alpha = max(alpha, value)

                if alpha >= beta:
                    break

            return column, value

        else:
            # Minimize player's score ...
            value = math.inf
            column = random.choice(valid_locations)

            for w in valid_locations:
                h = self.FindRow(table, w)
                b_copy = table.copy()

                b_copy[h][w] = self.PLAYER_PIECE
                new_score = self.AlphaBeta(b_copy, depth - 1, alpha, beta, True)[1]

                if new_score < value:
                    value = new_score
                    column = w

                beta = min(beta, value)

                if alpha >= beta:
                    break

            return column, value

    def GetMoves(self, table):
        valid_locations = []

        for w in range(self.cols):
            if table[self.rows - 1][w] == 0:
                valid_locations.append(w)

        return valid_locations

    def GetBestAction(self, table, piece):
        positions = self.GetMoves(table)
        best_score = -10000

        best_col = random.choice(positions)

        for w in positions:
            h = self.FindRow(table, w)
            temp_board = table.copy()

            temp_board[h][w] = piece
            score = self.score_position(temp_board, piece)

            if score > best_score:
                best_score = score
                best_col = w

        return best_col

    def GamePaint(self, table):
        for c in range(self.cols):
            for r in range(self.rows):
                pygame.draw.rect(table, self.BLUE, (c * self.BOX_SIZE, r * self.BOX_SIZE + self.BOX_SIZE, self.BOX_SIZE, self.BOX_SIZE))
                pygame.draw.circle(table, self.BLACK, (
                    int(c * self.BOX_SIZE + self.BOX_SIZE / 2), int(r * self.BOX_SIZE + self.BOX_SIZE + self.BOX_SIZE / 2)), self.RADIUS)

        for c in range(self.cols):
            for r in range(self.rows):
                if self.board[r][c] == self.PLAYER_PIECE:
                    pygame.draw.circle(table, self.RED, (
                        int(c * self.BOX_SIZE + self.BOX_SIZE / 2), self.height - int(r * self.BOX_SIZE + self.BOX_SIZE / 2)), self.RADIUS)
                elif self.board[r][c] == self.AI_PIECE:
                    pygame.draw.circle(table, self.YELLOW, (
                        int(c * self.BOX_SIZE + self.BOX_SIZE / 2), self.height - int(r * self.BOX_SIZE + self.BOX_SIZE / 2)), self.RADIUS)

        pygame.display.update()
