import pygame
import random
from time import sleep
from typing import TypeVar

# Colours
WHITE_COLOUR, ORANGE_COLOUR = (255, 255, 255), (255, 165, 0)
GREENYELLOW_COLOUR, POWDERBLUE_COLOUR = (173, 255, 47), (176, 224, 230)
DARKSEAGREEN_COLOUR, DARKGREEN_COLOUR = (143, 188, 143), (0,  100, 0)

# Sizes and Dimensions
CANVAS_DIMENSION = 600
BOARD_DIMENSION = 20
SQUARE_SIZE = CANVAS_DIMENSION/BOARD_DIMENSION - 1

# Time
TIME_TICK = 0.00

TSquare = TypeVar("TSquare", bound="Square")


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
        self.set_colour(WHITE_COLOUR)
        self.traversable = True

    def show(self) -> None:
        ''' Draws the square on the board with a little border'''
        if self.colour_changed:
            self.pygame.draw.rect(
                pygame.display.get_surface(),
                self.colour,
                self.pygame.Rect(
                    self.x_coordinate*(
                        SQUARE_SIZE+1),
                    self.y_coordinate*(
                        SQUARE_SIZE+1),
                    SQUARE_SIZE, SQUARE_SIZE))
        colour_changed = False

    def set_colour(self, new_colour: (int, int, int)) -> None:
        ''' Changes the square colour and signalizes it's
            colour has changed '''
        self.colour_changed = True
        self.colour = new_colour

    def get_coordinates(self) -> (int, int):
        return (self.y_coordinate, self.x_coordinate)

    def add_neighbour(self, neighbour_square: (int, int)) -> None:
        self.neighbours.append(neighbour_square)

    def add_parent(self, parent_square: TSquare) -> None:
        self.parent_square = parent_square

    def set_obstacle(self, is_obstacle: bool) -> None:
        self.traversable = not is_obstacle
        if not self.traversable:
            self.set_colour((0, 0, 0))


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
            self.add_diagonal_neighbours()
            self.set_random_obstacles(0.3)

        def show(self):
            ''' Prints all board squares on canvas '''
            for column in self.grid:
                for square in column:
                    square.show()
            pygame.display.update()

        def set_start(self, y_coordinate: int, x_coordinate: int) -> None:
            ''' Configure the square at given coordinates
                as the start square'''
            self.start_square = self.grid[y_coordinate][x_coordinate]
            self.start_square.set_colour(POWDERBLUE_COLOUR)
            self.start_square.set_obstacle(False)

        def set_end(self, y_coordinate: int, x_coordinate: int) -> None:
            ''' Configure the square at given coordinates as the end square '''
            self.end_square = self.grid[y_coordinate][x_coordinate]
            self.end_square.set_colour(ORANGE_COLOUR)
            self.end_square.set_obstacle(False)

        def add_adjacent_neighbours(self) -> None:
            ''' Add adjacent neighbours to all squares in grid '''
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

        def add_diagonal_neighbours(self) -> None:
            ''' Add diagonal neighbours to all squares in grid '''
            for column in self.grid:
                for square in column:
                    coordinates = square.get_coordinates()
                    for adjacent_index in [(-1, 1), (1, 1), (1, -1), (-1, 1)]:
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

        def set_random_obstacles(self, percentual_chance: int) -> None:
            for column in self.grid:
                for square in column:
                    if random.random() < percentual_chance:
                        square.set_obstacle(True)

        def a_star_pathfind(self, start: TSquare, goal: TSquare):
            ''' Following VibhakarMohta instructions available in geelsforgeeks
                Initialize the open list
                Initialize the closed list
                put the starting node on the open
                list '''
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
                open_list, found = self.a_star_search_neighbours(
                    q_node, goal, open_list, closed_list)
                if found is True:
                    return True
                closed_list.append(q_node)
            return False

        def get_square_at(self, coordinate: (int, int)) -> TSquare:
            ''' Returns the square available at given
                coordinate if it exists'''
            square = None
            if self.is_valid_coordinate(coordinate):
                square = self.grid[coordinate[0]][coordinate[1]]
            else:
                square = None
            return square

    instance = None

    def __init__(self, pygame, dimension: int) -> None:
        if not Board.instance:
            Board.instance = Board.__Board(pygame, dimension)

    def __getattr__(self, name):
        ''' Encapsules attributes for the singleton '''
        return getattr(self.instance, name)


def euclidean_distance(
        start_coordinate: (int, int),
        goal_coordinate: (int, int)) -> float:
    ''' Receives two coordinates (y, x) and return their distance using
    euclidean distance'''
    return (
        (goal_coordinate[0] - start_coordinate[0])**2 +
        (goal_coordinate[1] - start_coordinate[1])**2) ** (1/2)


def manhattan_distance(
        start_coordinate: (int, int),
        goal_coordinate: (int, int)) -> int:
    ''' Receives two coordinates (y, x) and return their manhattan
    distance '''
    return abs(goal_coordinate[0] - start_coordinate[0])\
        + abs(goal_coordinate[1] - start_coordinate[1])


def distance_between(
        first_node: TSquare,
        second_node: TSquare) -> int:
    ''' Receives two nodes and return their distance using
    euclidean distance'''
    return euclidean_distance(
        first_node.get_coordinates(), second_node.get_coordinates())


def a_star_pathfind(start: TSquare, goal: TSquare):
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
        open_list, found = a_star_search_neighbours(
            q_node, goal, open_list, closed_list)
        if found is True:
            return True
        closed_list.append(q_node)
    return False


def a_star_search_neighbours(
        q_node, goal, open_list, closed_list):
    ''' Search for selected node neighbours, calculate
        their distances and add then to open_list. If
        the end was found return open_list, True
        else open_list, False '''

    for neighbour in q_node.neighbours:
        ''' Generate sucessors and set their
            parents to q '''
        if neighbour.get_coordinates() == goal.get_coordinates():
            ''' if successor is the goal, stop search '''
            neighbour.add_parent(q_node)
            return open_list, True

        if neighbour in closed_list or not neighbour.traversable:
            continue
        temp_g = q_node.g + distance_between(q_node, neighbour)
        if neighbour in open_list:
            neighbour_index = open_list.index(neighbour)
            if temp_g > open_list[neighbour_index].g:
                continue
        neighbour.g = temp_g
        neighbour.add_parent(q_node)
        neighbour.h = manhattan_distance(
            neighbour.get_coordinates(), goal.get_coordinates())
        neighbour.f = neighbour.g + neighbour.h
        open_list.append(neighbour)

    show_board(open_list, closed_list)
    return open_list, False


def dijkstras_pathfinding(start: TSquare, goal: TSquare):
    ''' Similar to a star pathfinding but without the 
        heutistic function '''
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
        open_list, found = dijkstras_search_neighbours(
            q_node, goal, open_list, closed_list)
        if found is True:
            return True
        closed_list.append(q_node)
    return False


def dijkstras_search_neighbours(
        q_node, goal, open_list, closed_list):
    ''' Search for selected node neighbours, calculate
        their distances and add then to open_list. If
        the end was found return open_list, True
        else open_list, False '''

    for neighbour in q_node.neighbours:
        ''' Generate sucessors and set their
            parents to q '''
        if neighbour.get_coordinates() == goal.get_coordinates():
            ''' if successor is the goal, stop search '''
            neighbour.add_parent(q_node)
            return open_list, True

        if neighbour in closed_list or not neighbour.traversable:
            continue
        temp_g = q_node.g + distance_between(q_node, neighbour)
        if neighbour in open_list:
            neighbour_index = open_list.index(neighbour)
            if temp_g > open_list[neighbour_index].g:
                continue
        neighbour.g = temp_g
        neighbour.add_parent(q_node)
        neighbour.f = neighbour.g
        open_list.append(neighbour)

    show_board(open_list, closed_list)
    return open_list, False

def show_board(open_list, closed_list) -> None:
    ''' Show the board if there's already a board created '''
    board = Board(0, 0)
    for column in board.grid:
        for square in column:
            if square in open_list:
                square.set_colour(GREENYELLOW_COLOUR)
            elif square in closed_list:
                square.set_colour(DARKSEAGREEN_COLOUR)

    board.show()
    sleep(TIME_TICK)
