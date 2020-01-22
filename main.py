''' Main module of the pathfinding project.
Used to show graphic interface.
'''
import pygame
from time import time
from board import CANVAS_DIMENSION, BOARD_DIMENSION,\
    SQUARE_SIZE, OBSTACLES_RATIO, MENU_BAR_HEIGHT, WHITE_COLOUR
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
                if pos[0] > MENU_BAR_HEIGHT:
                    coordinates = (
                        int((pos[0]-MENU_BAR_HEIGHT)/SQUARE_SIZE),
                        int(pos[1]/SQUARE_SIZE))
                    clicked = True
                else:
                    coordinates = (int(pos[0]/5), int(pos[1]/100))
                    clicked = True
    return coordinates


available_algorithms = {
                "AST": ["a_star_pathfind"],
                "DIJ": ["dijkstras_pathfinding"],
                "DFS": ["shortest_path_dfs"],
                "BFS": ["shortest_path_bfs"]
                }


start_time = time()
pygame.init()

pygame_window = pygame.display.set_mode(
    (CANVAS_DIMENSION, CANVAS_DIMENSION + MENU_BAR_HEIGHT))
board = Board(pygame, BOARD_DIMENSION)

i = 0
for key in available_algorithms:
    available_algorithms[key].append(((i+1)*75, 5))
    pygame.draw.rect(
        pygame.display.get_surface(),
        WHITE_COLOUR,
        pygame.Rect(
            (i+1)*(100), 5,
            90, 30))
    i += 1

board.show()

# Choose which algorithm will run
coordinates = capture_click_position()
# Need to associate coordinates and functions dynamically
# Need to refactor here so it can be better modularized
# Need to refactor BFS, it's not working somehow
if coordinates[1] == 1:
    choosen_algorithm = available_algorithms['AST'][0]
elif coordinates[1] == 2:
    choosen_algorithm = available_algorithms['DIJ'][0]
elif coordinates[1] == 3:
    choosen_algorithm = available_algorithms['DFS'][0]
elif coordinates[1] == 4:
    choosen_algorithm = available_algorithms['BFS'][0]

print(choosen_algorithm)

coordinates = capture_click_position()
board.set_start(coordinates)
board.show()
for _ in range(2):
    coordinates = capture_click_position()
    board.set_end(coordinates)
    board.show()

# board.set_random_obstacles(0.5)
board.set_perlin_noise_obstacles(0.3)

path = []
partial_start = board.start_node
for goal in board.end_node:
    path_found = eval(choosen_algorithm+"(partial_start, goal)")
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
