''' Main module of the pathfinding project.
Used to show graphic interface.
'''
import pygame
from time import time
from board import CANVAS_DIMENSION, BOARD_DIMENSION,\
    DARKGREEN_COLOUR, TIME_TICK
from time import sleep
from board import Board, a_star_pathfind,\
  dijkstras_pathfinding, double_dijkstras_pathfinding, shortest_path_dfs

start_time = time()
pygame.init()


pygame_window = pygame.display.set_mode((CANVAS_DIMENSION, CANVAS_DIMENSION))
board = Board(pygame, BOARD_DIMENSION)
board.set_start(BOARD_DIMENSION//4, BOARD_DIMENSION//4)
board.set_end(BOARD_DIMENSION-1, BOARD_DIMENSION-1)
was_pathfound = shortest_path_dfs(board.start_square, board.end_square)
if was_pathfound:
    if board.end_square.parent_square is None:
        path_square = board.start_square
    elif board.start_square.parent_square is None:
        path_square = board.end_square
    while(path_square):
        path_square.set_colour(DARKGREEN_COLOUR)
        path_square = path_square.parent_square
        board.show()
        sleep(TIME_TICK*10)

board.show()
print("Time to find path: ", time() - start_time, " seconds")
pygame.quit()
