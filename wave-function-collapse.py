#!/usr/bin/env python3

import logging
import random
import curses
from collections import deque
import sys
sys.setrecursionlimit(1000000)

kernel = '''\
    ╻  ╻  ╻    
    ┗━━╋━━┛    
       ┃       
       ┃       
╺┓  ┏━━┻━━┓  ┏╸
 ┃  ┃     ┃  ┃ 
╺╋━━┫     ┣━━╋╸
 ┃  ┃     ┃  ┃ 
╺┛  ┗━━┳━━┛  ┗╸
       ┃       
       ┃       
    ┏━━╋━━┓    
    ╹  ╹  ╹    
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
        if x - 1 >= 0:
            rule = {r for char in cell for r in rules[char]['up']}
            update_cell(grid, x - 1, y, rule, queue, stdscr)
        if x + 1 < len(grid[y]):
            rule = {r for char in cell for r in rules[char]['down']}
            update_cell(grid, x + 1, y, rule, queue, stdscr)
        if y - 1 >= 0:
            rule = {r for char in cell for r in rules[char]['left']}
            update_cell(grid, x, y - 1, rule, queue, stdscr)
        if y + 1 < len(grid):
            rule = {r for char in cell for r in rules[char]['right']}
            update_cell(grid, x, y + 1, rule, queue, stdscr)
        update(grid, queue, stdscr)


def update_cell(grid, x, y, rule, queue, stdscr):
    if len(rule) == 0:
        return

    len_cell = len(grid[y][x])
    if len_cell > 1:
        grid[y][x] &= rule
        if len(grid[y][x]) < len_cell:
            queue.append((x, y))
            draw(grid, x, y, stdscr)


def main(stdscr):
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

    curses.curs_set(0)
    stdscr.getkey()


curses.wrapper(main)
