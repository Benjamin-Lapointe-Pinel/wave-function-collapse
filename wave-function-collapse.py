#!/usr/bin/env python3

import random
import curses

seed = '''
   ╻╻╻   
   ┗╋┛   
    ┃    
╺┓ ┏┻┓ ┏╸
╺╋━┫ ┣━╋╸
╺┛ ┗┳┛ ┗╸
    ┃    
   ┏╋┓   
   ╹╹╹   
'''

seed_line = seed.replace('\n', '')
char_set = list(set(seed_line))
char_weights = [seed_line.count(char) for char in char_set]


def main(stdscr):
    stdscr.clear()

    WIDTH = stdscr.getmaxyx()[1]
    HEIGHT = stdscr.getmaxyx()[0]
    WIDTH = 64
    HEIGHT = 32
    grid = [[char_set for _ in range(HEIGHT)] for _ in range(WIDTH)]

    for y in range(HEIGHT):
        for x in range(WIDTH):
            stdscr.insstr(y, x, '.')

    for _ in range(WIDTH * HEIGHT):
        entropy = [{'x': x, 'y': y, 'entropy': len(grid[x][y])} for x in range(len(grid)) for y in range(len(grid[x])) if len(grid[x][y]) > 1]
        min_entropy = min(entropy, key=lambda e: e['entropy'])['entropy']
        entropy = [e for e in entropy if e['entropy'] <= min_entropy]
        cell = random.choice(entropy)
        x = cell['x']
        y = cell['y']
        entropy = cell['entropy']
        index = random.choices(range(entropy), char_weights, k=1)[0]
        char = grid[x][y][index]
        grid[x][y] = [char]

        #TODO collapse

        try:
            stdscr.addstr(y, x, char)
        except curses.error:
            pass
        stdscr.refresh()

    curses.curs_set(0)
    stdscr.getkey()


curses.wrapper(main)
