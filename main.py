''' Main module of the pathfinding project.
Used to show graphic interface.
'''
import pygame
from time import time
from board import CANVAS_DIMENSION, BOARD_DIMENSION,\
    DARKGREEN_COLOUR, TIME_TICK
from time import sleep
from board import Board, a_star_pathfind,\
    dijkstras_pathfinding, double_dijkstras_pathfinding,\
    shortest_path_dfs, shortest_path_bfs, show_path


start_time = time()
pygame.init()


pygame_window = pygame.display.set_mode((CANVAS_DIMENSION, CANVAS_DIMENSION))
board = Board(pygame, BOARD_DIMENSION)
board.set_start(0, 0)
board.set_end((BOARD_DIMENSION-1), (BOARD_DIMENSION-1))
board.set_end((BOARD_DIMENSION-1)//2, (BOARD_DIMENSION-1)//2)

end_square = board.end_square.pop()
end_square_2 = board.end_square.pop()

path = dijkstras_pathfinding(board.start_square, end_square)
path = dijkstras_pathfinding(end_square, end_square_2) + path

if not path:
    print("No Path available")
else:
    show_path(path)

board.show()
print("Time to find path: ", time() - start_time, " seconds")
pygame.quit()



