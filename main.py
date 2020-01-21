''' Main module of the pathfinding project.
Used to show graphic interface.
'''
import pygame
from time import time
from board import CANVAS_DIMENSION, BOARD_DIMENSION,\
    SQUARE_SIZE, OBSTACLES_RATIO
from board import Board, a_star_pathfind,\
    dijkstras_pathfinding, double_dijkstras_pathfinding,\
    shortest_path_dfs, shortest_path_bfs, show_path


def capture_click_position() -> (int, int):
    ''' Waits for a click and returns the position
        on the board that it was make '''
    clicked = False
    while(not clicked):
        # get all events
        ev = pygame.event.get()

        # proceed events
        for event in ev:
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                pos = pos[::-1]
                coordinates = tuple(map(lambda x: int(x//SQUARE_SIZE), pos))
                clicked = True
    return coordinates


start_time = time()
pygame.init()

pygame_window = pygame.display.set_mode((CANVAS_DIMENSION, CANVAS_DIMENSION))
board = Board(pygame, BOARD_DIMENSION)
board.show()
coordinates = capture_click_position()
board.set_start(coordinates)
board.show()
for _ in range(3):
    coordinates = capture_click_position()
    board.set_end(coordinates)
    board.show()

board.set_random_obstacles(OBSTACLES_RATIO)

path = []
partial_start = board.start_node
for goal in board.end_node:
    path_found = a_star_pathfind(partial_start, goal)
    if not path_found:
        path = []
        break
    path = path_found + path
    partial_start = goal

if not path:
    print("No Path available")
else:
    show_path(path)

board.show()
print("Time to find path: ", time() - start_time, " seconds")
pygame.quit()
