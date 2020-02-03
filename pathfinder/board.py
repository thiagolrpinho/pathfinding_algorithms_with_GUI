import random
from time import sleep
from typing import List, TypeVar

import noise
import pygame

# Colours
WHITE_COLOUR, BLACK_COLOUR = (255, 255, 255), (0, 0, 0)
RED_COLOUR, ORANGE_COLOUR = (255, 0, 0), (255, 165, 0)
GREENYELLOW_COLOUR, POWDERBLUE_COLOUR = (173, 255, 47), (176, 224, 230)
DARKSEAGREEN_COLOUR, DARKGREEN_COLOUR = (143, 188, 143), (0,  100, 0)

# Sizes and Dimensions
CANVAS_DIMENSION = 500
BOARD_DIMENSION = 50
SQUARE_SIZE = int(CANVAS_DIMENSION/BOARD_DIMENSION)
MENU_BAR_HEIGHT = 100
NODE_SIZE = SQUARE_SIZE - 1
OBSTACLES_RATIO = 0.3


# Time
TIME_TICK = 0.01

# Algorithms related constants
AVAILABLE_ALGORITHMS = [
    "a_star_pathfind",
    "dijkstras_pathfinding"
]

TNode = TypeVar("TNode", bound="Node")


class Node():
    ''' Encapsules the boards nodes.
    Have X and Y coordinates, it's neibourghs
    and some attributes
    '''
    def __init__(self, pygame, y_coordinate: int, x_coordinate: int) -> None:
        self.pygame = pygame
        self.neighbours = set()
        self.parent_node = None
        self.special = False
        self.x_coordinate, self.y_coordinate = x_coordinate, y_coordinate
        self.g, self.h, self.f = 1, 1, 1
        self.set_colour(WHITE_COLOUR)
        self.traversable = True

    def show(self) -> None:
        ''' Draws the node on the board with a little border
            if it's colour has changed'''
        if self.colour_changed:
            self.pygame.draw.rect(
                pygame.display.get_surface(),
                self.colour,
                self.pygame.Rect(
                    self.x_coordinate*(SQUARE_SIZE),
                    MENU_BAR_HEIGHT + self.y_coordinate*(SQUARE_SIZE),
                    NODE_SIZE, NODE_SIZE))
            self.colour_changed = False

    def set_colour(self, new_colour: (int, int, int)) -> None:
        ''' Changes the node colour and signalizes it's
            colour has changed '''
        if not self.special:
            self.colour_changed = True
            self.colour = new_colour

    def get_coordinates(self) -> (int, int):
        return (self.y_coordinate, self.x_coordinate)

    def add_neighbour(self, neighbour_node: (int, int)) -> None:
        self.neighbours.add(neighbour_node)

    def add_parent(self, parent_node: TNode) -> None:
        self.parent_node = parent_node

    def set_obstacle(self, is_obstacle: bool) -> None:
        self.traversable = not is_obstacle
        if not self.traversable:
            self.set_colour(BLACK_COLOUR)
        elif not self.special:
            self.set_colour(WHITE_COLOUR)

    def set_special(self, is_special: bool) -> None:
        ''' Set a node as special, it's color
            can't be changed '''
        self.special = is_special


class Board():
    ''' Singleton for a board, it encapsules the visual representation of the
        board '''
    class __Board():
        def __init__(self, pygame, dimension: int) -> None:
            self.pygame = pygame
            weight, height = dimension, dimension
            self.start_node = None
            self.goal_nodes = []
            self.grid = [
                [Node(
                    pygame, y, x)
                    for x in range(weight)]
                for y in range(height)]
            self.add_adjacent_neighbours()
            self.add_diagonal_neighbours()

        def show(self):
            ''' Prints all board nodes on canvas '''
            for column in self.grid:
                for node in column:
                    node.show()
            pygame.display.update()

        def set_start(self, coordinates: (int, int)) -> None:
            ''' Configure the node at given coordinates
                as the start node. If it's not an already
                special node.
                If other node was already the start, the old
                start node becomes a normal node.'''
            node = self.get_node_at(coordinates)
            if node.special:
                return None
            if not self.start_node:
                self.start_node = node
                self.start_node.set_colour(POWDERBLUE_COLOUR)
                self.start_node.set_special(True)
                self.start_node.set_obstacle(False)
            else:
                self.remove_start_node()
                self.start_node = node
                self.start_node.set_colour(POWDERBLUE_COLOUR)
                self.start_node.set_special(True)
                self.start_node.set_obstacle(False)

        def remove_start_node(self) -> None:
            ''' Changes the start node to a normal node again '''
            if not self.start_node:
                return None
            self.start_node.set_special(False)
            self.start_node.set_colour(WHITE_COLOUR)
            self.start_node = None

        def add_goal(self, coordinates: (int, int)) -> None:
            ''' Add the node at given coordinates as an goal node
            if it's not already an special node(like a start node)'''
            node = self.get_node_at(coordinates)
            if not node.special:
                node.set_colour(ORANGE_COLOUR)
                node.set_special(True)
                node.set_obstacle(False)
                self.goal_nodes.append(node)
            elif node in self.goal_nodes:
                self.remove_goal(coordinates)

        def remove_goal(self, coordinates: (int, int)) -> None:
            ''' Remove given goal coordinate from goal nodes
                making it a normal square '''
            removed_goal_index = None
            removed_node = self.get_node_at(coordinates)
            for i, goal in enumerate(self.goal_nodes):
                if removed_node == goal:
                    goal.set_special(False)
                    goal.set_colour(WHITE_COLOUR)
                    removed_goal_index = i
                    break
            if removed_goal_index is not None:
                del self.goal_nodes[removed_goal_index]

        def clear_goals(self) -> None:
            ''' Clear all goals from board making then
                normal squares. '''
            for goal in self.goal_nodes:
                goal.set_special(False)
                goal.set_colour(WHITE_COLOUR)
            self.goal_nodes = []

        def add_adjacent_neighbours(self) -> None:
            ''' Add adjacent neighbours to all nodes in grid '''
            for column in self.grid:
                for node in column:
                    coordinates = node.get_coordinates()
                    for adjacent_index in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        possible_adjacent = tuple(
                            map(lambda x, y: x+y, coordinates, adjacent_index))
                        if self.is_valid_coordinate(possible_adjacent):
                            neighbour_node = self.get_node_at(
                                possible_adjacent)
                            node.add_neighbour(neighbour_node)

        def add_diagonal_neighbours(self) -> None:
            ''' Add diagonal neighbours to all nodes in grid '''
            for column in self.grid:
                for node in column:
                    coordinates = node.get_coordinates()
                    for adjacent_index in [(-1, -1), (1, 1), (1, -1), (-1, 1)]:
                        possible_adjacent = tuple(
                            map(lambda x, y: x+y, coordinates, adjacent_index))
                        if self.is_valid_coordinate(possible_adjacent):
                            neighbour_node = self.get_node_at(
                                possible_adjacent)
                            node.add_neighbour(neighbour_node)

        def is_valid_coordinate(self, possible_coordinate: (int, int)) -> bool:
            return sum(map(
                        lambda x: x < 0 or x >= BOARD_DIMENSION,
                        possible_coordinate)) == 0

        def alternate_obstacle_at(self, coordinate: (int, int)) -> None:
            node = self.get_node_at(coordinate)
            if node.traversable:
                node.set_obstacle(True)
            else:
                node.set_obstacle(False)

        def set_random_obstacles(self, percentual_chance: int) -> None:
            for column in self.grid:
                for node in column:
                    if random.random() < percentual_chance:
                        node.set_obstacle(True)

        def set_perlin_noise_obstacles(self, percentual_chance: int) -> None:
            seed = random.randint(0, 100)
            x_length = len(self.grid)
            y_length = len(self.grid[0])
            for i in range(x_length):
                for j in range(y_length):
                    noise_value = noise.snoise2(
                        i/x_length*3, j/y_length*3, 1, base=seed)
                    if (noise_value + 1)/2 < percentual_chance:
                        self.grid[i][j].set_obstacle(True)

        def get_node_at(self, coordinate: (int, int)) -> TNode:
            ''' Returns the node available at given
                coordinate if it exists'''
            node = None
            if self.is_valid_coordinate(coordinate):
                node = self.grid[coordinate[0]][coordinate[1]]
            else:
                node = None
            return node

        def clear_colours(self) -> None:
            ''' Clear all the normal board squares back to white.
                Do not affect speacial squares or obstacles'''
            for column in self.grid:
                for node in column:
                    if not node.special and node.traversable:
                        node.set_colour(WHITE_COLOUR)

        def clear(self) -> None:
            ''' Clear all the board squares. Like restarting it. '''
            self.remove_start_node()
            self.clear_goals()

            for column in self.grid:
                for node in column:
                    if not node.traversable:
                        self.alternate_obstacle_at(node.get_coordinates())
                    else:
                        node.set_colour(WHITE_COLOUR)
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
        first_node: TNode,
        second_node: TNode) -> int:
    ''' Receives two nodes and return their distance using
    euclidean distance'''
    return euclidean_distance(
        first_node.get_coordinates(), second_node.get_coordinates())


def a_star_pathfind(start: TNode, goal: TNode) -> List[TNode]:
    ''' Following VibhakarMohta instructions available in geelsforgeeks
        Initialize the open set
        Initialize the closed set
        put the starting node on the open set
    '''
    open_set = set()
    closed_set = set()
    start.parent_node = None
    open_set.add(start)
    while(open_set):
        ''' while the open list is not empty '''
        '''find the node with the least f on
        the open list, call it "q" '''
        q_node = min(open_set, key=lambda x: x.f)
        open_set.remove(q_node)
        ''' pop q off the open list '''
        open_set, found = a_star_search_neighbours(
            q_node, goal, open_set, closed_set)
        if found:
            path = extract_path(goal)
            return path
        closed_set.add(q_node)
    return []


def a_star_search_neighbours(
        q_node, goal, open_set, closed_set):
    ''' Search for selected node neighbours, calculate
        their distances and add then to open_set. If
        the end was found return open_set, True
        else open_set, False '''
    for neighbour in q_node.neighbours:
        ''' Generate sucessors and set their
            parents to q '''
        if neighbour.get_coordinates() == goal.get_coordinates():
            ''' if successor is the goal, stop search '''
            neighbour.add_parent(q_node)
            return open_set, True

        if neighbour in closed_set or not neighbour.traversable:
            continue
        temp_g = q_node.g + distance_between(q_node, neighbour)
        if neighbour in open_set:
            if temp_g > neighbour.g:
                continue
        neighbour.g = temp_g
        neighbour.add_parent(q_node)
        neighbour.h = manhattan_distance(
            neighbour.get_coordinates(), goal.get_coordinates())
        neighbour.f = neighbour.g + neighbour.h
        open_set.add(neighbour)
    show_board(open_set, closed_set)
    return open_set, False


def dijkstras_pathfinding(start: TNode, goal: TNode) -> List[TNode]:
    ''' Similar to a star pathfinding but without the
        heuristic function '''
    open_set = set()
    closed_set = set()
    start.parent_node = None
    open_set.add(start)
    while(open_set):
        ''' while the open list is not empty '''
        '''find the node with the least f on
        the open list, call it "q" '''
        q_node = min(open_set, key=lambda x: x.f)
        open_set.remove(q_node)
        ''' pop q off the open list '''
        open_set, found = dijkstras_search_neighbours(
            q_node, goal, open_set, closed_set)
        show_board(open_set, closed_set)

        if found:
            path = extract_path(goal)
            return path
        closed_set.add(q_node)
    return []


def dijkstras_search_neighbours(
        q_node, goal, open_set, closed_set):
    ''' Search for selected node neighbours, calculate
        their distances and add then to open_set. If
        the end was found return open_set, True
        else open_list, False '''
    for neighbour in q_node.neighbours:
        ''' Generate sucessors and set their
            parents to q '''
        if neighbour.get_coordinates() == goal.get_coordinates():
            ''' if successor is the goal, stop search '''
            neighbour.add_parent(q_node)
            return open_set, True

        if neighbour in closed_set or not neighbour.traversable:
            continue
        temp_g = q_node.g + distance_between(q_node, neighbour)
        if neighbour in open_set:
            if temp_g > neighbour.g:
                continue
        neighbour.g = temp_g
        neighbour.add_parent(q_node)
        neighbour.f = neighbour.g
        open_set.add(neighbour)
    return open_set, False


def show_board(open_set, closed_list) -> None:
    ''' Show the board if there's already a board created '''
    board = Board(0, 0)
    for node in open_set:
        if board.start_node != node and\
                node not in board.goal_nodes:
            node.set_colour(GREENYELLOW_COLOUR)
    for node in closed_list:
        if board.start_node != node and\
                node not in board.goal_nodes:
            node.set_colour(DARKSEAGREEN_COLOUR)

    board.show()
    sleep(TIME_TICK)


def extract_path(end_node: TNode) -> List[TNode]:
    ''' Recursiverly search on end_node to
        extract each node tha's part of path
        and returns it as a List '''
    if end_node.parent_node is None:
        print("Error following path")
        exit
    path_node = end_node
    path = []
    while(path_node):
        path.append(path_node)
        path_node = path_node.parent_node
    return path


def show_path(path_list: List[TNode]) -> None:
    ''' Recursiverly search on end_node to
        draw a path on the board '''
    board = Board(0, 0)
    if not path_list:
        print("Error following path")
        exit
    while(path_list):
        path_node = path_list.pop()
        path_node.set_colour(DARKGREEN_COLOUR)
        board.show()
        sleep(TIME_TICK*5)
