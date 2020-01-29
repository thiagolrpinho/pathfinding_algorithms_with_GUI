''' Main module of the pathfinding project.
Used to show graphic interface.
'''
import pygame
import os
from time import time
from board import CANVAS_DIMENSION, BOARD_DIMENSION,\
    SQUARE_SIZE, OBSTACLES_RATIO, MENU_BAR_HEIGHT,\
    BLACK_COLOUR, RED_COLOUR, AVAILABLE_ALGORITHMS
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
pygame.display.set_mode(
    (CANVAS_DIMENSION, CANVAS_DIMENSION + MENU_BAR_HEIGHT))
CLOCK = pygame.time.Clock()
FRAMES_PER_SECOND = 10
WAIT_TIME_MILISECONDS = 300
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


def show_wait_erase_icon_border(icon_choice: int) -> None:
    ''' Shows board. Waits for WAIT_TIME_MILISECONDS
        and then erase the border around the icon'''
    board.show()
    pygame.time.wait(WAIT_TIME_MILISECONDS)
    erase_icon_border(icon_choice)


def alternate_border_icon(icon_choice: int, should_draw: bool) -> None:
    ''' Draws or erases given icon based on should draw argument.
    '''
    if should_draw:
        draw_icon_border(icon_choice)
    else:
        erase_icon_border(icon_choice)


def run_pathfind_algorithm(pathfind_algorithm: str) -> None:
    ''' Executes the chosen pathfind algorithm and draws
        on board the found path if any was found.
    '''
    if not board.start_node or not board.goal_nodes:
        return None
    path = []
    partial_start = board.start_node
    for goal in board.goal_nodes:
        path_found = eval(pathfind_algorithm+"(partial_start, goal)")
        if not path_found:
            path = []
            break
        path = path_found + path
        partial_start = goal

    if not path:
        print("No Path available")
    else:
        show_path(path)

    pygame.time.wait(5*WAIT_TIME_MILISECONDS)
    board.clear()


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
        if icon_flags['obstacles'] == 1:
            board.set_random_obstacles(OBSTACLES_RATIO)
            show_wait_erase_icon_border(icon_choice)
        elif icon_flags['obstacles'] == 2:
            board.set_perlin_noise_obstacles(OBSTACLES_RATIO)
            show_wait_erase_icon_border(icon_choice)
    elif icon_choice < 12:
        if icon_choice == 7:
            ''' Alternate start button '''
            icon_flags['goal'] = False
            erase_icon_border(8)
            icon_flags['start'] = not icon_flags['start']
            alternate_border_icon(icon_choice, icon_flags['start'])
        elif icon_choice == 8:
            ''' Alternate goal button '''
            icon_flags['start'] = False
            erase_icon_border(7)
            icon_flags['goal'] = not icon_flags['goal']
            alternate_border_icon(icon_choice, icon_flags['goal'])
        elif icon_choice == 9:
            ''' Play button '''
            draw_icon_border(icon_choice)
            chosen_algorithm = AVAILABLE_ALGORITHMS[icon_flags['pathfind']]
            run_pathfind_algorithm(chosen_algorithm)
            erase_icon_border(icon_choice)
        elif icon_choice == 10:
            ''' Restart button '''
            draw_icon_border(icon_choice)
            board.clear()
            show_wait_erase_icon_border(icon_choice)
        else:
            ''' Close button '''
            draw_icon_border(icon_choice)
            show_wait_erase_icon_border(icon_choice)
            icon_flags['finish'] = True
    return icon_flags


def draw_icon_border(icon_choice: int) -> None:
    '''Receives the index of the chosen icon
        and draws around it a red rectangle border'''
    start_x = icon_choice*BUTTON_AREA_LENGTH - 5
    start_y = int(BUTTON_AREA_HEIGTH/2) - 5
    x_length = BUTTON_AREA_LENGTH + 5
    y_length = BUTTON_AREA_HEIGTH + 10
    rectangle = [start_x, start_y, x_length, y_length]
    pygame.draw.rect(SURFACE, RED_COLOUR, rectangle, 2)


def erase_icon_border(icon_choice: int) -> None:
    ''' Receives the index of one chosen icon
        and erasesthe border around it'''
    start_x = icon_choice*BUTTON_AREA_LENGTH - 5
    start_y = int(BUTTON_AREA_HEIGTH/2) - 5
    x_length = BUTTON_AREA_LENGTH + 5
    y_length = BUTTON_AREA_HEIGTH + 10
    rectangle = [start_x, start_y, x_length, y_length]
    pygame.draw.rect(SURFACE, BLACK_COLOUR, rectangle, 2)

icon_flags = {
    "play": False,
    "start": False,
    "goal": False,
    "pathfind": 0,
    "obstacles": 0,
    "finish": False
}

start_time = time()
draw_menu_bar(AVAILABLE_ALGORITHMS)
board = Board(pygame, BOARD_DIMENSION)
draw_icon_border(0)
draw_icon_border(4)

board.show()

while not icon_flags['finish']:
    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    CLOCK.tick(FRAMES_PER_SECOND)

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
                is_higher_than_start_icon_height =\
                    pos[0] >= int(BUTTON_AREA_HEIGTH/2)
                is_lower_than_maximum_icon_height =\
                    pos[0] <= MENU_BAR_HEIGHT - int(BUTTON_AREA_HEIGTH/2)
                if is_higher_than_start_icon_height and\
                        is_lower_than_maximum_icon_height:
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

print("Time running app: ", time() - start_time, " seconds")
pygame.quit()
