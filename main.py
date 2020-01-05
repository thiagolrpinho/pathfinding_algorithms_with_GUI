''' Main module of the pathfinding project.
Used to show graphic interface.
'''
import pygame
from typing import TypeVar
from math import hypot # Using this for euclidean distance

TSquare = TypeVar("TSquare", bound="Square")

WHITE_COLOUR, ORANGE_COLOUR = (255, 255, 255), (255, 165, 0)
GREENYELLOW_COLOUR, POWDERBLUE_COLOUR = (173, 255, 47), (176, 224, 230)
DARKSEAGREEN_COLOUR = (143, 188, 143)

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
                            neighbour = self.grid[
                                possible_adjacent[0]][possible_adjacent[1]]
                            square.add_neighbour(neighbour)

        def is_valid_coordinate(self, possible_coordinate: (int, int)) -> bool:
            return sum(map(
                        lambda x: x < 0 or x >= BOARD_DIMENSION,
                        possible_coordinate)) == 0

        def a_start_pathfinding(
                self,
                start: TSquare,
                goal: TSquare,
                heuristic_function: str = 'euclidean_dist') -> bool:
            ''' Finds the best path fron start to goal using
            the heuristic function choosen. It paints the
            board square black for the path choosen. Returns
            True if able to find solution and False if not '''
            choosen_key = start.get_coordinates()
            openSet = {}
            closedSet = {}
            openSet[choosen_key] = start
            cameFrom = {}

            for square in openSet.values():
                print(square)
                square.set_colour(GREENYELLOW_COLOUR)
            for square in closedSet.values():
                square.set_colour(DARKSEAGREEN_COLOUR)
            self.show()

            for key in openSet.keys():
                if openSet[key].f < openSet[choosen_key].f:
                    choosen_key = key

                if openSet[choosen_key] == goal:
                    return True
                
                closedSet[choosen_key] = openSet.pop(choosen_key)
                for neighbour in closedSet[choosen_key].neighbours:
                    if neighbour.get_coordinates in closedSet:
                        continue
                    tentative_g_score = closedSet[choosen_key].g + 1
                    if neighbour.get_coordinates in openSet:
                        if tentative_g_score < neighbour.g:
                            neighbour.g_score = tentative_g_score
                    else:
                        neighbour.g = tentative_g_score
                        openSet[neighbour.get_coordinates()] = neighbour

                    neighbour.h = self.euclidean_distance(
                        neighbour.get_coordinates(), goal.get_coordinates())
                    neighbour.f = neighbour.h\
                        + neighbour.g

        def euclidean_distance(
                self,
                start_coordinates: (int, int),
                goal_coordinates: (int, int)) -> int:
            return hypot(
                goal_coordinates[0] - start_coordinates[0],
                goal_coordinates[1] - start_coordinates[0])

        


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

    def add_neighbour(self, neighbour_square: TSquare) -> None:
        self.neighbours.append(neighbour_square)


pygame_window = pygame.display.set_mode((CANVAS_DIMENSION, CANVAS_DIMENSION))
board = Board(pygame, BOARD_DIMENSION)
board.set_start(0, 0)
board.set_end(BOARD_DIMENSION-1, BOARD_DIMENSION-1)
board.show()
board.a_start_pathfinding(board.start_square, board.end_square)
board.show()

pygame.quit()
