# Preprocessor of board data from .game files.
# Data will be split among 100 files, each with the format of:
# 3 flattened lists describing either black, white or empty
# 8 flattened lists describing liberties
# 4 flattened lists describing the number of turns since a move was played.

# => 15 flattened lists
# => 1 line for target

import os

import copy
import time

import numpy as np

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

def preprocess(path):
    board_size = 19
    # Split the data between one hundred files

    files = []
    for i in range (1):
        files.append(open('split-games/split' + str(i) + '.data', 'w'))

    for g in os.listdir('stripped-games')[0:10]:
        print ("Opening " + os.path.join('stripped-games', g))

        game = open(os.path.join('stripped-games', g), 'r')
        moves = game.readlines()[1:]
        game.close()

        stones = np.zeros([board_size, board_size]) - 1
        turns_since = np.zeros([board_size, board_size])
        liberties_board = np.zeros([board_size, board_size])
        start = time.time()
        for m in range (len(moves)):
            player = moves[m][0] == 'W'
            move = [ord(moves[m][1]) - 97, ord(moves[m][2]) - 97]

            stones[move[0]][move[1]] = player
            turns_since[move[0]][move[1]] += 1

            # Go through all stones

            strings = []
            visited = set()
            for y in range (board_size):
                for x in range (board_size):
                    #where's the for (int i = 0; i < dick.length(); i++)
                    # because it's an infinite loop

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
                                turns_since[s[0]][s[1]] = 0
                                liberties_board[s[0]][s[1]] = 0
                        else:
                            for s in strings[-1][1:]:
                                liberties_board[s[0]][s[1]] = strings[-1][0]


            # X = stones


            # Pick a dataset and write
            dataset = 0
            f = files[dataset]
        print(time.time() - start)
            #f.write(np.array2string(stones) + '\n')

    for f in files:
        f.close()

preprocess('stripped-games')
