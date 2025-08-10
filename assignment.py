import random

SAVE_FILENAME = 'savegame.txt'
MAP_FILENAME = 'level1.txt'

def read_map(filename):
    #open and read from the file
    try:
        with open(filename, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip('') is not None]
    except Exception:
        # backup!!! if my txt isnt working :(
        lines = [
            "T CCCCC SS GGG",
            " CCCCC SSSS",
            "GGG",
            " CCCC SSSS GGG",
            " SSSSS CCC",
            " CC S CCCC",
            "CCCCCCCCC CCCCC",
            "CCCCCCCC G CCCC",
            " CCCCC GG SS",
            " CCCCC GGG",
            "SSSSSS",
            " CCC GGG",
            "SSSGGG",
        ]
    # maxw → Finds the length of the longest row.
    #Loops over every row and if it’s shorter than maxw, adds spaces at the end so all rows have equal length.
    #This ensures the map have a perfect rectangle grid 
    grid = [list(line) for line in lines]
    maxw = max(len(r) for r in grid)
    for r in grid:
        if len(r) < maxw:
            r.extend([' '] * (maxw - len(r)))
    return grid

def find_tile(grid, tile): 
    #basically finds a certain character and gives me coords
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == tile:
                return (x, y)
    return None