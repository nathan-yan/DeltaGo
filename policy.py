# Policy network for BetaGo

import threading
import queue

import numpy as np
import keras
from keras.models import Sequential

import time
import copy
import os

import pygame
import pygame.gfxdraw
from pygame.locals import *

data_q = queue.Queue(maxsize = 10000)

def fill_queue(path, epochs, board_size = 19):
    """ fill_queue(path, epochs, board_size = 19) -> None
    fills a queue asynchronously with data from professional Go games.
    This thread fills the queue as fast as it can, and starts by randomly selecting 100 random games (this excludes them from being chosen until the next epoch), and playing them out in random order.
    """

    for epoch in range (epochs):
        game_files = np.array(os.listdir(path))

        # While game_files isn't empty
        while game_files.shape[0]:
            # Select 100 random game files, if the length of the game_files is less than 100, break
            if len(game_files) < 100:
                break;
            else:
                selected_games = np.random.randint(0, len(game_files), 100)

            files = game_files[selected_games]
            game_files = np.delete(game_files, selected_games)

            game_data = []
            game_boards = []
            game_lengths = []
            game_progress = []
            for g in files:
                f = open(os.path.join(path, g), 'r')
                game_data.append(f.readlines()[1:])
                game_boards.append(np.zeros([board_size, board_size]) - 1)
                game_lengths.append(len(game_data[-1]))
                game_progress.append(0)
                f.close()

            while game_data:
                time.sleep(0.01)
                if data_q.qsize() < (9000):
                    try:
                #print(data_q.qsize())
                        chose = np.random.randint(0, len(game_data))
                        if game_lengths[chose] <= 2:
                            del game_data[chose]
                            del game_boards[chose]
                            del game_lengths[chose]
                            del game_progress[chose]
                            continue;

                        else:

                            # Pick the next move
                            inp, target, game_boards[chose] = add_to(game_boards[chose],
                            game_data[chose][game_progress[chose]], game_data[chose][game_progress[chose] + 1])

                            #display(inp)


                            game_progress[chose] += 1
                            game_lengths[chose] -= 1

                            if game_lengths[chose] <= 2:
                                del game_data[chose]
                                del game_boards[chose]
                                del game_lengths[chose]
                                del game_progress[chose]
                                continue;

                            data_q.put([inp, target], block = True)
                            #pygame.display.flip()
                            #pygame.event.get()
                            #print("INSERTED")
                    except Exception as ex:
                        print("thread-1 failed:", ex, game_data[chose][game_progress[chose]], game_data[chose][game_progress[chose] + 1])
                        continue;

    data_q.put(['DONE', 'DONE'], block = True)

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

def add_to(board, move, future_move, board_size = 19):
    player = move[0] == 'W'
    move = [ord(move[1]) - 97, ord(move[2]) - 97]
    f_move = [ord(future_move[1]) - 97, ord(future_move[2]) - 97]

    board[move[0]][move[1]] = player

    # Go through all stones

    strings = []
    visited = set()
    for y in range (board_size):
        for x in range (board_size):
            # Check amount of liberties
            if (y * board_size + x) not in visited and board[y][x] != -1:
                liberties, connections = num_liberties([y, x], board)

                stoneQ = queue.Queue()
                for c in connections:
                    stoneQ.put(c)

                strings.append([liberties, [y, x]])
                visited.add(y * board_size + x)

                while not stoneQ.empty():
                    examining = stoneQ.get()
                    visited.add(examining[0] * board_size + examining[1])

                    strings[-1].append(examining)

                    liberties, connections = num_liberties(examining, board)
                    strings[-1][0] += liberties
                    for c in connections:
                        if c[0] * board_size + c[1] not in visited:
                            stoneQ.put(c)

                if strings[-1][0] == 0:
                    for s in strings[-1][1:]:
                        board[s[0]][s[1]] = -1

    return_board = np.zeros([4, board_size, board_size])
    return_target = np.zeros([1, board_size, board_size])

    return_target[0][f_move[0]][f_move[1]] = 1

    for y in range (board_size):
        for x in range (board_size):
            # If white just played (policy is predicting for black), any white stones are placed on feature map 2 (0-indexed) and black stones are placed on feature map 1

            # However, if black just played (policy is predicting for white), any white stones are placed on feature map 1 (0-indexed) and black stones are placed on feature map 2

            # Empty intersections are always on feature map 0
            # Feature map 3 is reserved for boundary management.
            if player:
                return_board[int(board[y][x] + 1)][y][x] = 1
            else:
                if board[y][x] == -1:
                    return_board[0][y][x] = 1
                else:
                    return_board[int(2 - board[y][x])][y][x] = 1

    return return_board, return_target.flatten(), board

def draw_lines(screen, screen_width = 760, lines = 17):
    for x in range (lines + 2):
        pygame.draw.line(screen, (200, 200, 200), (x * 760/(lines + 2), 0), (x * 760/(lines + 2), screen_width))
    for y in range ((lines + 2)):
        pygame.draw.line(screen, (200, 200, 200), (0, y * 760/(lines + 2)), (screen_width, y * 760/(lines + 2)))

def circle(surface, color, pos, radius, fill = True):
    pos = [int(pos[0]), int(pos[1])]
    color = [np.clip(int(color[0]), 0, 255), np.clip(int(color[1]), 0, 255), np.clip(int(color[2]), 0, 255)]
    radius = int(radius)
    pygame.gfxdraw.aacircle(surface, pos[0], pos[1], radius, color)

    if fill:
        pygame.gfxdraw.filled_circle(surface, pos[0], pos[1], radius, color)

def display(stones, board_size = 19):
    square_size = int(760/19)
    screen.fill((100, 100, 100))

    draw_lines(screen, 760, board_size - 2)

    for y in range (board_size):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        for x in range (board_size):
            if stones[0][y][x]:
                player = -1
            elif stones[1][y][x]:
                player = 0
            elif stones[2][y][x]:
                player = 1
            if player != -1:
                circle(screen, (255 * player, 255 * player, 255 * player), ((y + 1) * square_size , (x + 1) * square_size ), 15)

    pygame.display.flip()

def display_(stones, evaluation, target, screen, board_size = 19):
    square_size = int(760/19)
    screen.fill((100, 100, 100))

    draw_lines(screen, 760, board_size - 2)

    for y in range (board_size):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        for x in range (board_size):
            if stones[0][y][x]:
                player = -1
            elif stones[1][y][x]:
                player = 0
            elif stones[2][y][x]:
                player = 1
            if player != -1:
                circle(screen, (255 * player, 255 * player, 255 * player), ((y + 1) * square_size , (x + 1) * square_size ), 15)

            if target[y][x]:
                circle(screen, (0, 255, 0), ((y + 1) * square_size , (x + 1) * square_size ), 10)

            if (evaluation[y][x] > 0.01):
                circle(screen, (255 - 255 * evaluation[y][x], 255 - 255 * evaluation[y][x], 255 - 100 * evaluation[y][x]), ((y + 1) * square_size , (x + 1) * square_size ), 15 * evaluation[y][x])
                circle(screen, (255, 255, 255), ((y + 1) * square_size , (x + 1) * square_size ), 15, fill = False)

    pygame.display.flip()

if __name__ == "__main__":
    from keras.models import load_model
    fill = threading.Thread(target = fill_queue, args = ('stripped-games', 1))
    fill.start()

    #model = Sequential()
    #model.add(keras.layers.convolutional.Conv2D(filters = 129, kernel_size = 5, padding = 'same', use_bias = True, input_shape = (4, 19, 19), activation = 'relu', data_format = 'channels_first'))

    #for i in range (10):
    #    model.add(keras.layers.convolutional.Conv2D(filters = 129, kernel_size = 5, padding = 'same', use_bias = True, activation = 'relu', data_format = 'channels_first'))

    #model.add(keras.layers.convolutional.Conv2D(filters = 1, kernel_size = 1, padding = 'same', use_bias = True, data_format = 'channels_first'))

    #model.add(keras.layers.core.Flatten())

    #model.add(keras.layers.Activation('softmax'))

    #model.compile(optimizer = keras.optimizers.RMSprop(lr = 0.0001), loss = 'categorical_crossentropy', metrics = ['accuracy'])

    model = load_model('checkpoints/model_6001.h5')

    # pop 32 elements from our queue

    screen = pygame.display.set_mode((760, 760))
    c = 0
    while True:
        for event in pygame.event.get():
            if event == pygame.QUIT:
                pygame.quit()

        batch_x = []
        batch_y = []

        for b in range (32):
            inp, tar = data_q.get(block = True)

            if inp == "DONE" or tar == "DONE":
                break;

            batch_x.append(inp)
            batch_y.append(tar)

        l, a = model.train_on_batch(np.array(batch_x), np.array(batch_y))
        test = np.array(model.predict(np.array([batch_x[0]]), batch_size = 1)).reshape([19, 19])

        print(l, a)

        c += 1
        if c % 10 == 1:
            display_(batch_x[0], test, np.array(batch_y[0]).reshape([19, 19]), screen)

        if c % 1000 == 1:
            if l > 7:
                del model
                model = load_model('checkpoints/model_' + str(c + 7000 - 1000) + '.h5')
            else:
                model.save('checkpoints/model_' + str(c) + '.h5')

    fill.join()

#fill_queue('stripped-games', 1)
