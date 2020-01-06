''' Main module of the pathfinding project.
Used to show graphic interface.
'''
import pygame
from typing import TypeVar, Tuple
from time import sleep

TSquare = TypeVar("TSquare", bound="Square")
TCoordinate = Tuple[int, int]

WHITE_COLOUR, ORANGE_COLOUR = (255, 255, 255), (255, 165, 0)
GREENYELLOW_COLOUR, POWDERBLUE_COLOUR = (173, 255, 47), (176, 224, 230)
DARKSEAGREEN_COLOUR, DARKGREEN_COLOUR = (143, 188, 143), (0,  100, 0)

CANVAS_DIMENSION = 400
BOARD_DIMENSION = 50
SQUARE_SIZE = CANVAS_DIMENSION/BOARD_DIMENSION - 1

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
                            neighbour_square = self.get_square_at(
                                possible_adjacent)
                            square.add_neighbour(neighbour_square)

        def is_valid_coordinate(self, possible_coordinate: (int, int)) -> bool:
            return sum(map(
                        lambda x: x < 0 or x >= BOARD_DIMENSION,
                        possible_coordinate)) == 0

        def a_star_pathfind(self, start: TSquare, goal: TSquare):
            ''' Following VibhakarMohta instructions available in geelsforgeeks
                Initialize the open list
                Initialize the closed list
                put the starting node on the open
                list
            '''
            open_list = []
            closed_list = []

            open_list.append(start)
            while(open_list):
                ''' while the open list is not empty '''
                open_list.sort(key=lambda x: x.f, reverse=True)
                '''find the node with the least f on
                the open list, call it "q" '''
                q_node = open_list.pop()
                ''' pop q off the open list '''
                for neighbour in q_node.neighbours:
                    ''' Generate sucessors and set their
                        parents to q '''
                    if neighbour.get_coordinates() == goal.get_coordinates():
                        ''' if successor is the goal, stop search '''
                        neighbour.add_parent(q_node)
                        return True

                    if neighbour in closed_list:
                        continue
                    neighbour.add_parent(q_node)
                    temp_g = q_node.g + 1
                    if neighbour in open_list:
                        neighbour_index = open_list.index(neighbour)
                        if temp_g > open_list[neighbour_index].g:
                            continue
                    neighbour.g = temp_g
                    neighbour.h = self.manhattan_distance(
                        neighbour.get_coordinates(), goal.get_coordinates())
                    neighbour.f = neighbour.g + neighbour.h
                    open_list.append(neighbour)
                    for column in self.grid:
                        for square in column:
                            if square in open_list:
                                square.set_colour(GREENYELLOW_COLOUR)
                            elif square in closed_list:
                                square.set_colour(DARKSEAGREEN_COLOUR)

                    self.show()
                    sleep(0.05)
                closed_list.append(q_node)
            return False

        def get_square_at(self, coordinate: (int, int)) -> TSquare:
            return self.grid[coordinate[0]][coordinate[1]]

        def euclidean_distance(
                self,
                start_coordinate: (int, int),
                goal_coordinate: (int, int)) -> int:
            ''' Receives two coordinates (y, x) and return their distance using
            euclidean distance'''
            return (
                (goal_coordinate[0] - start_coordinate[0])**2 +
                (goal_coordinate[1] - start_coordinate[1])**2) ** (1/2)

        def manhattan_distance(
                self,
                start_coordinate: (int, int),
                goal_coordinate: (int, int)) -> int:
            ''' Receives two coordinates (y, x) and return their manhattan
            distance '''
            return abs(goal_coordinate[0] - start_coordinate[0])\
                + abs(goal_coordinate[1] - start_coordinate[1])

        def distance_between(
                self, first_node: TSquare, second_node: TSquare) -> int:
            ''' Receives two nodes and return their distance using
            euclidean distance'''
            return self.euclidean_distance(
                first_node.get_coordinates(), second_node.get_coordinates())
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
        self.parent_square = None
        self.x_coordinate, self.y_coordinate = x_coordinate, y_coordinate
        self.g, self.h, self.f = 1, 1, 1
        self.colour = WHITE_COLOUR

    def show(self) -> None:
        ''' Draws the square on the board with a little border'''
        self.pygame.draw.rect(
            pygame.display.get_surface(),
            self.colour,
            self.pygame.Rect(
                self.x_coordinate*(
                    SQUARE_SIZE+1),
                self.y_coordinate*(
                    SQUARE_SIZE+1),
                SQUARE_SIZE, SQUARE_SIZE))

    def set_colour(self, new_colour: (int, int, int)) -> None:
        self.colour = new_colour

    def get_coordinates(self) -> (int, int):
        return (self.y_coordinate, self.x_coordinate)

    def add_neighbour(self, neighbour_square: (int, int)) -> None:
        self.neighbours.append(neighbour_square)

    def add_parent(self, parent_square: TSquare) -> None:
        self.parent_square = parent_square


pygame_window = pygame.display.set_mode((CANVAS_DIMENSION, CANVAS_DIMENSION))
board = Board(pygame, BOARD_DIMENSION)
board.set_start(0, 0)
board.set_end(BOARD_DIMENSION-2, BOARD_DIMENSION-2)
was_pathfound = board.a_star_pathfind(board.start_square, board.end_square)
if was_pathfound:
    path_square = board.end_square
    while(path_square):
        path_square.set_colour(DARKGREEN_COLOUR)
        path_square = path_square.parent_square
        sleep(0.1)
        board.show()
board.show()
pygame.quit()
