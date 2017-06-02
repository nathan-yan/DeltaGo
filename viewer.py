import pygame
from pygame.locals import *
from pygame import gfxdraw

import numpy as np

import copy
import time

class Queue:
    def __init__(self):
        self.queue = []

    def push(self, value):
        self.queue.append(value)

    def pop(self):
        tmp = self.queue[0]
        del self.queue[0]

        return tmp

    def is_empty(self):
        return not self.queue

def draw_lines(screen, screen_width = 760, lines = 17):
    for x in range (lines + 2):
        pygame.draw.line(screen, (200, 200, 200), (x * 760/(lines + 2), 0), (x * 760/(lines + 2), screen_width))
    for y in range ((lines + 2)):
        pygame.draw.line(screen, (200, 200, 200), (0, y * 760/(lines + 2)), (screen_width, y * 760/(lines + 2)))

def circle(surface, color, pos, radius):
    pos = [int(pos[0]), int(pos[1])]
    radius = int(radius)
    pygame.gfxdraw.aacircle(surface, pos[0], pos[1], radius, color)
    pygame.gfxdraw.filled_circle(surface, pos[0], pos[1], radius, color)

def num_liberties(pos, board):
    board_size = len(board)

    liberties = 4

    player = board[pos[0]][pos[1]]

    permutations = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    connections = []

    for permutation in permutations:
        if (pos[0] + permutation[0]) >= board_size or (pos[0] + permutation[0]) < 0 or (pos[1] + permutation[1]) >= board_size or (pos[1] + permutation[1]) < 0:
            liberties -= 1
            continue;
        elif board[pos[0] + permutation[0]][pos[1] + permutation[1]] == -1:
            pass
        elif board[pos[0] + permutation[0]][pos[1] + permutation[1]] != player:
            liberties -= 1
        elif board[pos[0] + permutation[0]][pos[1] + permutation[1]] == player:
            connections.append([pos[0] + permutation[0], pos[1] + permutation[1]])
            liberties -= 1

    return liberties, connections

def viewer(game, board_size = 20):
    pygame.init()

    game = open(game, 'r')
    moves = game.readlines()[1:]
    current_move = 0

    stones = np.zeros([board_size, board_size]) - 1
    boards = []

    square_size = int(760/20)

    screen = pygame.display.set_mode((760, 760))
    screen.fill((100, 100, 100))
    draw_lines(screen, 760, board_size - 2)

    can_press = True

    s = time.time
    for m in range (len(moves)):
        player = moves[m][0] == 'W'
        move = [ord(moves[m][1]) - 97, ord(moves[m][2]) - 97]

        stones[move[0]][move[1]] = player

        # Go through all stones

        strings = []
        visited = set()
        for y in range (board_size):
            for x in range (board_size):
                # Check amount of liberties
                if (y * board_size + x) not in visited and stones[y][x] != -1:
                    liberties, connections = num_liberties([y, x], stones)

                    stoneQ = Queue()
                    for c in connections:
                        stoneQ.push(c)

                    strings.append([liberties, [y, x]])
                    visited.add(y * board_size + x)

                    while not stoneQ.is_empty():
                        examining = stoneQ.pop()
                        visited.add(examining[0] * board_size + examining[1])

                        strings[-1].append(examining)

                        liberties, connections = num_liberties(examining, stones)
                        strings[-1][0] += liberties
                        for c in connections:
                            if c[0] * board_size + c[1] not in visited:
                                stoneQ.push(c)

                    if strings[-1][0] == 0:
                        for s in strings[-1][1:]:
                            stones[s[0]][s[1]] = -1

        boards.append(copy.deepcopy(stones))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN :
                if event.key == pygame.K_LEFT:
                    # Go back a move
                    stones = copy.deepcopy(boards[current_move - 1])
                    screen.fill((100, 100, 100))
                    draw_lines(screen, 760, board_size - 2)

                    for y in range (board_size):
                        for x in range (board_size):
                            player = stones[y][x]
                            if player != -1:
                                circle(screen, (255 * player, 255 * player, 255 * player), ((y + 1) * square_size , (x + 1) * square_size ), 15)

                    current_move -= 1

                elif event.key == pygame.K_RIGHT:
                    if current_move + 1 >= len(moves):
                        continue

                    # Go back a move
                    stones = copy.deepcopy(boards[current_move + 1])
                    screen.fill((100, 100, 100))
                    draw_lines(screen, 760, board_size - 2)

                    for y in range (board_size):
                        for x in range (board_size):
                            player = stones[y][x]
                            if player != -1:
                                circle(screen, (255 * player, 255 * player, 255 * player), ((y + 1) * square_size , (x + 1) * square_size ), 15)

                    current_move += 1

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    # Go back a move
                    stones = copy.deepcopy(boards[current_move - 1])
                    screen.fill((100, 100, 100))
                    draw_lines(screen, 760, board_size - 2)

                    for y in range (board_size):
                        for x in range (board_size):
                            player = stones[y][x]
                            if player != -1:
                                circle(screen, (255 * player, 255 * player, 255 * player), ((y + 1) * square_size , (x + 1) * square_size ), 15)

                    current_move -= 1
                elif event.button == 5:
                    if current_move + 1 >= len(moves):
                        continue

                    # Go back a move
                    stones = copy.deepcopy(boards[current_move + 1])
                    screen.fill((100, 100, 100))
                    draw_lines(screen, 760, board_size - 2)

                    for y in range (board_size):
                        for x in range (board_size):
                            player = stones[y][x]
                            if player != -1:
                                circle(screen, (255 * player, 255 * player, 255 * player), ((y + 1) * square_size , (x + 1) * square_size ), 15)

                    current_move += 1


        pygame.display.flip()

viewer('stripped-games/2016-03-10a.game')
