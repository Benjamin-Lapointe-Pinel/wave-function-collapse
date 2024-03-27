#!/usr/bin/env python3

import random
import curses

kernel = '''
   ╻ ╻ ╻   
   ┗━╋━┛   
     ┃     
╺┓ ┏━┻━┓ ┏╸
╺╋━┫   ┣━╋╸
╺┛ ┗━┳━┛ ┗╸
     ┃     
   ┏━╋━┓   
   ╹ ╹ ╹   
'''

kernel_line = kernel.replace('\n', '')
weighted_superposition = {char: kernel_line.count(char) for char in set(kernel_line)}


def get_least_entropy_coordinate(grid):
    entropy = [{'x': x, 'y': y, 'entropy': len(grid[x][y])} for x in range(len(grid)) for y in range(len(grid[x])) if len(grid[x][y]) > 1]
    min_entropy = min(entropy, key=lambda e: e['entropy'])['entropy']
    cells = [(e['x'], e['y']) for e in entropy if e['entropy'] <= min_entropy]
    return random.choice(cells)


def collapse(grid, x, y, stdscr):
    superposition = grid[x][y]
    weights = [weighted_superposition[s] for s in superposition]
    char = random.choices(superposition, weights, k=1)[0]
    grid[x][y] = [char]
    try:
        stdscr.addstr(y, x, char)
    except curses.error:
        pass
    stdscr.refresh()

    # TODO collapse recursive


def main(stdscr):
    stdscr.clear()

    WIDTH = stdscr.getmaxyx()[1]
    HEIGHT = stdscr.getmaxyx()[0]
    WIDTH = 64
    HEIGHT = 32
    grid = [[list(weighted_superposition.keys()) for _ in range(HEIGHT)] for _ in range(WIDTH)]

    for y in range(HEIGHT):
        for x in range(WIDTH):
            stdscr.insstr(y, x, '.')

    for _ in range(WIDTH * HEIGHT):
        x, y = get_least_entropy_coordinate(grid)
        collapse(grid, x, y, stdscr)

    curses.curs_set(0)
    stdscr.getkey()


curses.wrapper(main)
