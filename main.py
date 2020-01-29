''' Main module of the pathfinding project.
Used to show graphic interface.
'''
import pygame
import os
from time import time
from board import CANVAS_DIMENSION, BOARD_DIMENSION,\
    SQUARE_SIZE, OBSTACLES_RATIO, MENU_BAR_HEIGHT,\
        WHITE_COLOUR, BLACK_COLOUR, RED_COLOUR
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
MENU_BAR_CORNER_SIZE = 10
BUTTON_AREA_LENGTH = int(
    (CANVAS_DIMENSION)/TOTAL_NUMBER_OF_BUTTONS)
BUTTON_LENGTH = int(9/10 * BUTTON_AREA_LENGTH)
BUTTON_AREA_HEIGTH = int(MENU_BAR_HEIGHT/2)

# PATHS
ICONS_FOLDER_PATH = "assets/icons/"

# PYGAME RELATED GLOBALS CONSTANT
pygame.init()
CLOCK = pygame.time.Clock()
pygame.display.set_mode(
    (CANVAS_DIMENSION, CANVAS_DIMENSION + MENU_BAR_HEIGHT))
SURFACE = pygame.display.get_surface()

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
    ''' Function draws icons on the menu bar'''
    for i, icon_name in enumerate(IMAGE_ICON_LIST_NAMES):
        # For each icon we load it's image
        icon = pygame.image.load(os.path.join(ICONS_FOLDER_PATH + icon_name))
        icon.convert()
        # Then we rescale it to the current size
        rescaled_icon = pygame.transform.scale(
            icon, (BUTTON_LENGTH, BUTTON_AREA_HEIGTH))
        # We calculate where to draw it
        coordinate_to_draw_on = (
            i*BUTTON_AREA_LENGTH,
            int(BUTTON_AREA_HEIGTH/2))
        # And then draw the icon in the correct coordinate
        SURFACE.blit(rescaled_icon, coordinate_to_draw_on)
        pygame.display.flip()


def icon_click(
        icon_choice: int,
        icon_flags: dict) -> dict:
    ''' Receives an icon_choice and a dict with the actual states
        of the icon chosen and returns the new states. '''
    if icon_choice < 4:
        ''' Pathfinding algorithms buttons '''
        erase_icon_border(icon_flags['pathfind'])
        icon_flags['pathfind'] = icon_choice
        draw_icon_border(icon_choice)
    elif icon_choice < 7:
        ''' Obstacles algorithms buttons '''
        erase_icon_border(icon_flags['obstacles'] + 4)
        icon_flags['obstacles'] = icon_choice - 4
        draw_icon_border(icon_choice)
    elif icon_choice < 11:
        if icon_choice == 7:
            ''' Alternate start button '''
            icon_flags['goal'] = False
            erase_icon_border(8)
            icon_flags['start'] = not icon_flags['start']
            if icon_flags['start']:
                draw_icon_border(icon_choice)
            else:
                erase_icon_border(icon_choice)
        elif icon_choice == 8:
            ''' Alternate goal button '''
            icon_flags['start'] = False
            erase_icon_border(7)
            icon_flags['goal'] = not icon_flags['goal']
            if icon_flags['goal']:
                draw_icon_border(icon_choice)
            else:
                erase_icon_border(icon_choice)
        elif icon_choice == 9:
            ''' Play button '''
            icon_flags['play'] = True
    return icon_flags


def draw_icon_border(icon_choice: int) -> None:
    '''Receives the index of the chosen icon
        and draws around it a red rectangle border'''
    start_x = icon_choice*BUTTON_AREA_LENGTH
    start_y = int(BUTTON_AREA_HEIGTH/2)
    x_length = BUTTON_AREA_LENGTH
    y_length = BUTTON_AREA_HEIGTH
    rectangle = [start_x, start_y, x_length, y_length]
    pygame.draw.rect(SURFACE, RED_COLOUR, rectangle, 2)


def erase_icon_border(icon_choice: int) -> None:
    ''' Receives the index of one chosen icon
        and erasesthe border around it'''
    start_x = icon_choice*BUTTON_AREA_LENGTH
    start_y = int(BUTTON_AREA_HEIGTH/2)
    x_length = BUTTON_AREA_LENGTH
    y_length = BUTTON_AREA_HEIGTH
    rectangle = [start_x, start_y, x_length, y_length]
    pygame.draw.rect(SURFACE, BLACK_COLOUR, rectangle, 2)


available_algorithms = {
    "AST": ["a_star_pathfind"],
    "DIJ": ["dijkstras_pathfinding"],
    "DFS": ["shortest_path_dfs"],
    "BFS": ["shortest_path_bfs"],
    "RNG": ["set_random_obstacles"],
    "PRL": ["set_perlin_noise_obstacles"],
    "MNL": [""],
    "START": ["set_start"],
    "GOAL": ["add_goal"],
    "EXIT": [""]
}


icon_flags = {
    "play": False,
    "start": False,
    "goal": False,
    "pathfind": 0,
    "obstacles": 0
}

start_time = time()


draw_menu_bar(available_algorithms)
board = Board(pygame, BOARD_DIMENSION)

board.show()

while not icon_flags['play']:
    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    CLOCK.tick(10)

    # get all events
    ev = pygame.event.get()
    # proceed events
    for event in ev:
        if event.type == pygame.MOUSEBUTTONUP:
            ''' We are only interested in mouse clicks events '''
            pos = pygame.mouse.get_pos()
            pos = pos[::-1]
            ''' There are two types of clicks'''
            ''' on the board or on the menu bar '''
            if pos[0] <= MENU_BAR_HEIGHT:
                ''' On menu bar '''
                if pos[0] >= int(BUTTON_AREA_HEIGTH/2) and\
                        pos[0] <= MENU_BAR_HEIGHT - int(BUTTON_AREA_HEIGTH/2):
                    ''' If it's on an icon height '''
                    icon_choice = int(
                        pos[1]/(BUTTON_AREA_LENGTH))
                    ''' We then calculate which button was chosen '''
                    icon_flags = icon_click(icon_choice, icon_flags)
            else:
                ''' If the click was on the board '''
                coordinate = (
                    int((pos[0]-MENU_BAR_HEIGHT)/SQUARE_SIZE),
                    int(pos[1]/SQUARE_SIZE))
                if icon_flags['start']:
                    board.set_start(coordinate)
                elif icon_flags['goal']:
                    board.add_goal(coordinate)
                elif icon_flags['obstacles'] == 0:
                    board.alternate_obstacle_at(coordinate)
    board.show()


# Choose which algorithm will run
coordinates = capture_click_position()
# Need to associate coordinates and functions dynamically
# Need to refactor here so it can be better modularized
# Need to refactor BFS, it's not working somehow
if coordinates[1] == 1:
    chosen_algorithm = available_algorithms['AST'][0]
elif coordinates[1] == 2:
    chosen_algorithm = available_algorithms['DIJ'][0]
elif coordinates[1] == 3:
    chosen_algorithm = available_algorithms['DFS'][0]
elif coordinates[1] == 4:
    chosen_algorithm = available_algorithms['BFS'][0]

print(chosen_algorithm)

coordinates = capture_click_position()
board.set_start(coordinates)
board.show()
for _ in range(2):
    coordinates = capture_click_position()
    board.add_goal(coordinates)
    board.show()

# board.set_random_obstacles(0.5)
board.set_perlin_noise_obstacles(0.3)

path = []
partial_start = board.start_node
for goal in board.end_node:
    path_found = eval(chosen_algorithm+"(partial_start, goal)")
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
