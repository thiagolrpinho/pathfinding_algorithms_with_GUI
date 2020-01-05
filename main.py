''' Main module of the pathfinding project.
Used to show graphic interface.
'''
import pygame
from typing import TypeVar
from math import hypot  # Using this for euclidean distance
import time  # Using this to control the interface speed

TSquare = TypeVar("TSquare", bound="Square")

WHITE_COLOUR, ORANGE_COLOUR = (255, 255, 255), (255, 165, 0)
GREENYELLOW_COLOUR, POWDERBLUE_COLOUR = (173, 255, 47), (176, 224, 230)
DARKSEAGREEN_COLOUR, DARKGREEN_COLOUR = (143, 188, 143), (0,  100, 0)

CANVAS_DIMENSION = 400
BOARD_DIMENSION = 5
SQUARE_SIZE = CANVAS_DIMENSION/BOARD_DIMENSION

pygame.init()


class Board():
    ''' Singleton for a board, it encapsules the visual representation of the
    board '''
    class __Board():
        def __init__(self, pygame, dimension: int) -> None:
            self.pygame = pygame
            weight, height = dimension, dimension
            self.grid = [
                [Square(
                    pygame, y, x)
                    for x in range(weight)]
                for y in range(height)]
            self.add_adjacent_neighbours()

        def show(self):
            ''' Prints all board squares on canvas '''
            for column in self.grid:
                for square in column:
                    square.show()
            pygame.display.update()

        def set_start(self, y_coordinate: int, x_coordinate: int) -> None:
            self.start_square = self.grid[y_coordinate][x_coordinate]
            self.start_square.set_colour(POWDERBLUE_COLOUR)

        def set_end(self, y_coordinate: int, x_coordinate: int) -> None:
            self.end_square = self.grid[y_coordinate][x_coordinate]
            self.end_square.set_colour(ORANGE_COLOUR)

        def add_adjacent_neighbours(self) -> None:
            for column in self.grid:
                for square in column:
                    coordinates = square.get_coordinates()
                    for adjacent_index in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        possible_adjacent = tuple(
                            map(lambda x, y: x+y, coordinates, adjacent_index))
                        if self.is_valid_coordinate(possible_adjacent):
                            square.add_neighbour(possible_adjacent)

        def is_valid_coordinate(self, possible_coordinate: (int, int)) -> bool:
            return sum(map(
                        lambda x: x < 0 or x >= BOARD_DIMENSION,
                        possible_coordinate)) == 0

        def get_square_at(self, coordinate: (int, int)) -> TSquare:
            return self.grid[coordinate[0]][coordinate[1]]

        def a_start_pathfinding(
                self,
                start: TSquare,
                goal: TSquare,
                heuristic_function: str = 'euclidean_dist') -> bool:
            ''' Finds the best path fron start to goal using
            the heuristic function choosen. It paints the
            board square black for the path choosen. Returns
            True if able to find solution and False if not '''
            openSet = []
            closedSet = []
            openSet.append(start.get_coordinates())
            cameFrom = {}

            choosen_index = 0
            for i, _ in enumerate(openSet):
                choosen_square = self.get_square_at(openSet[choosen_index])
                temp_square = self.get_square_at(openSet[i])

                if temp_square.f < choosen_square.f:
                    choosen_index = i

                if openSet[choosen_index] == goal.get_coordinates():
                    return True

                current_coordinate = openSet[choosen_index]
                current_square = self.get_square_at(current_coordinate)

                openSet.pop(choosen_index)
                closedSet.append(current_coordinate)

                for neighbour_coordinate in current_square.neighbours:
                    if neighbour_coordinate in closedSet:
                        continue

                    neighbour_square = self.get_square_at(neighbour_coordinate)
                    tentative_g_score = current_square.g + 1
                    if neighbour_coordinate in openSet:
                        if tentative_g_score < neighbour_square.g:
                            neighbour_square.g_score = tentative_g_score
                    else:
                        neighbour_square.g = tentative_g_score
                        openSet.append(neighbour_coordinate)

                    neighbour_square.h = self.euclidean_distance(
                        neighbour_coordinate, goal.get_coordinates())
                    neighbour_square.f = neighbour_square.h\
                        + neighbour_square.g
                    neighbour_square.previous_square = current_square

                    for square_coordinate in openSet:
                        # painting all open set squares
                        square = self.get_square_at(square_coordinate)
                        square.set_colour(DARKSEAGREEN_COLOUR)
                    for square_coordinate in closedSet:
                        # painting all closed set squares
                        square = self.get_square_at(square_coordinate)
                        square.set_colour(GREENYELLOW_COLOUR)
                    # painting all path squares
                    while(current_square.previous_square):
                        current_square.set_colour(DARKGREEN_COLOUR)
                        current_square = current_square.previous_square
                    self.show()
                    time.sleep(0.5)
            return False

        def euclidean_distance(
                self,
                start_coordinate: (int, int),
                goal_coordinate: (int, int)) -> int:
            return hypot(
                goal_coordinate[0] - start_coordinate[0],
                goal_coordinate[1] - start_coordinate[0])

    instance = None

    def __init__(self, pygame, dimension: int) -> None:
        if not Board.instance:
            Board.instance = Board.__Board(pygame, dimension)

    def __getattr__(self, name):
        ''' Encapsules attributes for the singleton '''
        return getattr(self.instance, name)


class Square():
    ''' Encapsules the boards squares. 
    Have X and Y coordinates, it's neibourghs
    and some attributes
    '''
    def __init__(self, pygame, y_coordinate: int, x_coordinate: int) -> None:
        self.pygame = pygame
        self.neighbours = []
        self.previous_square = None
        self.x_coordinate, self.y_coordinate = x_coordinate, y_coordinate
        self.g, self.h, self.f = 1, 1, 1
        self.colour = WHITE_COLOUR

    def show(self) -> None:
        ''' Draws the square on the board with a little border'''
        self.pygame.draw.rect(
            pygame.display.get_surface(),
            self.colour,
            self.pygame.Rect(
                self.x_coordinate*(SQUARE_SIZE+1),
                self.y_coordinate*(SQUARE_SIZE+1),
                SQUARE_SIZE, SQUARE_SIZE))

    def set_colour(self, new_colour: (int, int, int)) -> None:
        self.colour = new_colour

    def get_coordinates(self) -> (int, int):
        return (self.y_coordinate, self.x_coordinate)

    def add_neighbour(self, neighbour_coordinate: TSquare) -> None:
        self.neighbours.append(neighbour_coordinate)

pygame_window = pygame.display.set_mode((CANVAS_DIMENSION, CANVAS_DIMENSION))
board = Board(pygame, BOARD_DIMENSION)
board.set_start(0, 0)
board.set_end(BOARD_DIMENSION-1, BOARD_DIMENSION-1)
board.show()
print( board.a_start_pathfinding(board.start_square, board.end_square))
board.show()

pygame.quit()
