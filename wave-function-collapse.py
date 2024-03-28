#!/usr/bin/env python3

import logging
import random
import curses
from collections import deque

kernel = '''\
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
rules = {char: {'weight': kernel_line.count(char), 'up': set(), 'down': set(), 'left': set(), 'right': set()} for char in set(kernel_line)}
kernel_matrix = kernel.splitlines()
for y in range(len(kernel_matrix)):
    for x in range(len(kernel_matrix[y])):
        char = kernel_matrix[y][x]
        if x - 1 >= 0:
            rules[char]['left'].add(kernel_matrix[y][x - 1])
        if x + 1 < len(kernel_matrix[y]):
            rules[char]['right'].add(kernel_matrix[y][x + 1])
        if y - 1 >= 0:
            rules[char]['up'].add(kernel_matrix[y - 1][x])
        if y + 1 < len(kernel_matrix):
            rules[char]['down'].add(kernel_matrix[y + 1][x])

logging.basicConfig(level=logging.DEBUG, filename='wave-function-collapse.log', filemode='w', format='%(message)s')
for char in rules:
    logging.debug('\n')
    logging.debug(f"'{char}'")
    for key in rules[char].keys():
        logging.debug(f"{key: <6} : {rules[char][key]}")


def draw(grid, x, y, stdscr):
    cell = grid[x][y]
    if len(cell) == 0:
        char = '!'
    elif len(cell) == 1:
        char = cell[0]
    if char:
        try:
            stdscr.addstr(y, x, char)
        except curses.error:
            pass
        stdscr.refresh()


def get_least_entropy_coordinate(grid):
    entropy = [{'x': x, 'y': y, 'entropy': len(grid[x][y])} for x in range(len(grid)) for y in range(len(grid[x])) if len(grid[x][y]) > 1]
    min_entropy = min(entropy, key=lambda e: e['entropy'])['entropy']
    cells = [(e['x'], e['y']) for e in entropy if e['entropy'] <= min_entropy]
    return random.choice(cells)


def get_neighbors(grid, x, y):
    coordinates = []
    if x - 1 >= 0:
        coordinates.append((x - 1, y))
    if x + 1 < len(grid):
        coordinates.append((x + 1, y))
    if y - 1 >= 0:
        coordinates.append((x, y - 1))
    if y + 1 < len(grid[x]):
        coordinates.append((x, y + 1))
    return coordinates


def collapse(grid, x, y, stdscr):
    superposition = grid[x][y]
    weights = [rules[s]['weight'] for s in superposition]
    char = random.choices(superposition, weights, k=1)[0]
    grid[x][y] = [char]
    draw(grid, x, y, stdscr)

    update(grid, deque(get_neighbors(grid, x, y)))


def update(grid, queue):
    if queue:
        coordinate = queue.pop()

        update(grid, queue)


def main(stdscr):
    stdscr.clear()

    WIDTH = stdscr.getmaxyx()[1]
    HEIGHT = stdscr.getmaxyx()[0]
    WIDTH = 64
    HEIGHT = 32
    grid = [[list(rules.keys()) for _ in range(HEIGHT)] for _ in range(WIDTH)]

    for y in range(HEIGHT):
        for x in range(WIDTH):
            stdscr.insstr(y, x, '.')

    for _ in range(WIDTH * HEIGHT):
        x, y = get_least_entropy_coordinate(grid)
        collapse(grid, x, y, stdscr)

    curses.curs_set(0)
    stdscr.getkey()


curses.wrapper(main)
