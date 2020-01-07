''' Main module of the pathfinding project.
Used to show graphic interface.
'''
import pygame
from time import sleep
from gui_helper import CANVAS_DIMENSION, BOARD_DIMENSION, DARKGREEN_COLOUR, TIME_TICK
from board import Board


pygame.init()


pygame_window = pygame.display.set_mode((CANVAS_DIMENSION, CANVAS_DIMENSION))
board = Board(pygame, BOARD_DIMENSION)
board.set_start(2, 5)
board.set_end(BOARD_DIMENSION-2, BOARD_DIMENSION-2)
was_pathfound = board.a_star_pathfind(board.start_square, board.end_square)
if was_pathfound:
    path_square = board.end_square
    while(path_square):
        path_square.set_colour(DARKGREEN_COLOUR)
        path_square = path_square.parent_square
        sleep(TIME_TICK*2)
        board.show()
board.show()
pygame.quit()
