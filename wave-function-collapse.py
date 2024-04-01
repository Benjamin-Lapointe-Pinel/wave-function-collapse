#!/usr/bin/env python3

import logging
import random
import curses
from collections import deque
import sys
sys.setrecursionlimit(100000)

kernel = '''\
    ┃  ┃  ┃    
    ┗━━╋━━┛    
       ┃       
       ┃       
━┓  ┏━━┻━━┓  ┏━
 ┃  ┃     ┃  ┃ 
━╋━━┫     ┣━━╋━
 ┃  ┃     ┃  ┃ 
━┛  ┗━━┳━━┛  ┗━
       ┃       
       ┃       
    ┏━━╋━━┓    
    ┃  ┃  ┃    
'''

# kernel = '''\
#     
#  ┏┓ 
#  ┗┛ 
#     
# '''

# kernel = '''\
# ━┳┻┳━
# ━┻┳┻━
# '''

kernel_line = kernel.replace('\n', '')
kernel_set = set(kernel_line)
rules = {char: {'weight': kernel_line.count(char), 'up': set(), 'down': set(), 'left': set(), 'right': set()} for char in kernel_set}
rules['!'] = {'weight': 0, 'up': kernel_set, 'down': kernel_set, 'left': kernel_set, 'right': kernel_set}
kernel_matrix = kernel.splitlines()
for y in range(len(kernel_matrix)):
    for x in range(len(kernel_matrix[y])):
        char = kernel_matrix[y][x]
        rules[char]['left'].add(kernel_matrix[y][x - 1])
        rules[char]['up'].add(kernel_matrix[y - 1][x])
        rules[char]['right'].add(kernel_matrix[y][(x + 1) % len(kernel_matrix[y])])
        rules[char]['down'].add(kernel_matrix[(y + 1) % len(kernel_matrix)][x])

logging.basicConfig(level=logging.DEBUG, filename='wave-function-collapse.log', filemode='w', format='%(message)s')
for char in rules:
    logging.debug('\n')
    logging.debug(f"'{char}'")
    for key in rules[char].keys():
        logging.debug(f"{key: <6} : {rules[char][key]}")


def draw(grid, x, y, stdscr):
    cell = grid[y][x]
    char = '?'
    if len(cell) == 0:
        char = '!'
    elif len(cell) == 1:
        char = list(cell)[0]
    try:
        stdscr.addstr(x, y, char)
    except curses.error:
        pass
    stdscr.refresh()


def get_least_entropy_coordinate(grid):
    entropy = [{'x': x, 'y': y, 'entropy': len(grid[y][x])} for y in range(len(grid)) for x in range(len(grid[y])) if len(grid[y][x]) > 1]

    if len(entropy) == 0:
        return None, None

    min_entropy = min(entropy, key=lambda e: e['entropy'])['entropy']
    cells = [(e['x'], e['y']) for e in entropy if e['entropy'] <= min_entropy]
    cell = random.choice(cells)

    return cell


def collapse(grid, x, y, stdscr):
    superposition = list(grid[y][x])
    weights = [rules[s]['weight'] for s in superposition]
    char = random.choices(superposition, weights, k=1)[0]
    grid[y][x] = set(char)
    draw(grid, x, y, stdscr)

    update(grid, deque([(x, y)]), stdscr)
    # stdscr.getkey()

    for y in range(len(grid)):
        for x in range(len(grid[y])):
            cell = grid[y][x]
            if len(cell) > 1:
                try:
                    stdscr.addstr(x, y, '.')
                except curses.error:
                    pass
    stdscr.refresh()


def update(grid, queue, stdscr):
    if queue:
        x, y = queue.popleft()
        cell = grid[y][x]
        rule = {r for char in cell for r in rules[char]['up']}
        update_cell(grid, len(grid[y]) - 1 if x - 1 < 0 else x - 1, y, rule, queue, stdscr)
        rule = {r for char in cell for r in rules[char]['left']}
        update_cell(grid, x, len(grid) - 1 if y - 1 < 0 else y - 1, rule, queue, stdscr)
        rule = {r for char in cell for r in rules[char]['down']}
        update_cell(grid, (x + 1) % len(grid[y]), y, rule, queue, stdscr)
        rule = {r for char in cell for r in rules[char]['right']}
        update_cell(grid, x, (y + 1) % len(grid), rule, queue, stdscr)
        update(grid, queue, stdscr)


def update_cell(grid, x, y, rule, queue, stdscr):
    len_cell = len(grid[y][x])
    if len_cell > 1:
        grid[y][x] &= rule
        if len(grid[y][x]) < len_cell:
            if len(grid[y][x]) == 0:
                grid[y][x] = ['!']
            queue.append((x, y))
            draw(grid, x, y, stdscr)


def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()

    WIDTH = stdscr.getmaxyx()[1]
    HEIGHT = stdscr.getmaxyx()[0]
    # WIDTH = 64
    # HEIGHT = 32
    grid = [[set(rules.keys()) for _ in range(HEIGHT)] for _ in range(WIDTH)]

    for y in range(HEIGHT):
        for x in range(WIDTH):
            stdscr.insstr(y, x, '.')

    while True:
        x, y = get_least_entropy_coordinate(grid)
        if x is None or y is None:
            break
        collapse(grid, x, y, stdscr)

    stdscr.getkey()


curses.wrapper(main)
