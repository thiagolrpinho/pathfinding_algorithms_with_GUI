''' Main module of the pathfinding project.
Used to show graphic interface.
'''
import pygame
from time import time
from board import CANVAS_DIMENSION, BOARD_DIMENSION,\
    DARKGREEN_COLOUR, TIME_TICK
from time import sleep
from board import Board, a_star_pathfind,\
  dijkstras_pathfinding

start_time = time()
pygame.init()


pygame_window = pygame.display.set_mode((CANVAS_DIMENSION, CANVAS_DIMENSION))
board = Board(pygame, BOARD_DIMENSION)
board.set_start(BOARD_DIMENSION//2, BOARD_DIMENSION//2)
board.set_end(BOARD_DIMENSION-2, BOARD_DIMENSION-2)
was_pathfound = dijkstras_pathfinding(board.start_square, board.end_square)
if was_pathfound:
    path_square = board.end_square
    while(path_square):
        path_square.set_colour(DARKGREEN_COLOUR)
        path_square = path_square.parent_square
        board.show()
        sleep(TIME_TICK)

board.show()
print("Time to find path: ", time() - start_time, " seconds")
pygame.quit()
