''' Main module of the pathfinding project.
Used to show graphic interface.
'''
import pygame
import os
from time import time
from board import CANVAS_DIMENSION, BOARD_DIMENSION,\
    SQUARE_SIZE, OBSTACLES_RATIO, MENU_BAR_HEIGHT, WHITE_COLOUR
from board import Board, a_star_pathfind,\
    dijkstras_pathfinding, double_dijkstras_pathfinding,\
    shortest_path_dfs, shortest_path_bfs, show_path

IMAGE_ICON_LIST_NAMES = [
    "1_created_by_roundicons.png", "2_created_by_roundicons.png",
    "3_created_by_roundicons.png", "4_created_by_roundicons.png",
    "roman_1_created_by_roundicons.png", "roman_2_created_by_roundicons.png",
    "roman_3_created_by_roundicons.png", "start_created_by_freepik.png",
    "goal_created_by_freepik.png", "play_created_by_freepik.png",
    "rewind_created_by_freepik.png", "power_created_by_freepik.png"
]

# UI related sizes
TOTAL_NUMBER_OF_BUTTONS = len(IMAGE_ICON_LIST_NAMES)
BUTTON_AREA_LENGTH = int(
    (CANVAS_DIMENSION-SQUARE_SIZE)/TOTAL_NUMBER_OF_BUTTONS)
BUTTON_SIZE = BUTTON_AREA_LENGTH - 1

# PATHS
ICONS_FOLDER_PATH = "assets/icons/"

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


def draw_menu_bar(menu_choices) -> None:
    surface = pygame.display.get_surface()
    number_of_choices = len(menu_choices)
    for i, icon_name in enumerate(IMAGE_ICON_LIST_NAMES):
        print(icon_name)
        icon = pygame.image.load(os.path.join(ICONS_FOLDER_PATH + icon_name))
        icon.convert()
        surface.blit(pygame.transform.scale(
            icon, (BUTTON_AREA_LENGTH, 2*SQUARE_SIZE)),
            (int(SQUARE_SIZE/2)+i*BUTTON_AREA_LENGTH, int(SQUARE_SIZE/2)))
        pygame.display.flip()


available_algorithms = {
    "AST": ["a_star_pathfind"],
    "DIJ": ["dijkstras_pathfinding"],
    "DFS": ["shortest_path_dfs"],
    "BFS": ["shortest_path_bfs"],
    "RNG": ["set_random_obstacles"],
    "PRL": ["set_perlin_noise_obstacles"],
    "MNL": [""],
    "START": ["set_start"],
    "GOAL": ["set_end"],
    "EXIT": [""]
}


start_time = time()
pygame.init()

pygame_window = pygame.display.set_mode(
    (CANVAS_DIMENSION, CANVAS_DIMENSION + MENU_BAR_HEIGHT))
draw_menu_bar(available_algorithms)
board = Board(pygame, BOARD_DIMENSION)


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
