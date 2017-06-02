import os

import re
def find(s, substring, br = 1):
    b = 0
    idx = []
    l = len(substring)
    for i in range (len(s) - 3):
        if s[i : i + l] == substring:
            b += 1
            idx.append(i)

            if b == br:
                return idx

    return idx

def extract(path):
    for year in os.listdir(path):
        for game in os.listdir(os.path.join(path, year)):
            final_path = os.path.join(path, year, game)

            stripped = open('stripped-games/' + game[:-3] + 'game', 'w')
            original = open(final_path, 'r')

            print("Opening " + final_path)

            read = original.read()
            result_idx = find(read, 'RE[')[0]
            result = read[result_idx + 3:result_idx + 4]

            stripped.write(result + '\n')

            move_idx = find(read, ';', br = 10000)
            for i in move_idx[1:]:
                #print move_idx[i + 1] + move_idx[i + 2 : i + 4] )
                stripped.write(read[i + 1] + read[i + 3 : i + 5] + '\n')

            stripped.close()
            original.close()

            #return

extract('Games')
