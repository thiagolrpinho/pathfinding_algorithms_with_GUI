import random
from time import sleep
from typing import List, Set, TypeVar, Tuple

import random
import noise
import pygame
import numpy
from graph_tool.all import Graph

# Colours
WHITE_COLOUR, BLACK_COLOUR = (255, 255, 255), (0, 0, 0)
RED_COLOUR, ORANGE_COLOUR = (255, 0, 0), (255, 165, 0)
GREENYELLOW_COLOUR, POWDERBLUE_COLOUR = (173, 255, 47), (176, 224, 230)
DARKSEAGREEN_COLOUR, DARKGREEN_COLOUR = (143, 188, 143), (0,  100, 0)
PURPLE_COLOUR = (130, 46, 255)

# Sizes and Dimensions
CANVAS_DIMENSION = 500
BOARD_DIMENSION = 50
SQUARE_SIZE = int(CANVAS_DIMENSION/BOARD_DIMENSION)
MENU_BAR_HEIGHT = 100
NODE_SIZE = SQUARE_SIZE - 1
OBSTACLES_RATIO = 0.3


# Time
TIME_TICK = 0.05

# Algorithms related constants
AVAILABLE_ALGORITHMS = [
    "a_star_pathfind",
    "monte_carlo_pathfind",
    "dijkstras_pathfinding",
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
        self.t, self.n, self.child_nodes_num_monte_carlo = 0, 0, 0
        self.parent_monte_carlo = None
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

    def set_colour(self, new_colour: Tuple[int, int, int]) -> None:
        ''' Changes the node colour and signalizes it's
            colour has changed '''
        if not self.special:
            self.colour_changed = True
            self.colour = new_colour

    def get_coordinates(self) -> Tuple[int, int]:
        return (self.y_coordinate, self.x_coordinate)

    def add_neighbour(self, neighbour_node: Tuple[int, int]) -> None:
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
            self.dimension = dimension
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

        def set_start(self, coordinates: Tuple[int, int]) -> None:
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

        def add_goal(self, coordinates: Tuple[int, int]) -> None:
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

        def remove_goal(self, coordinates: Tuple[int, int]) -> None:
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

        def is_valid_coordinate(
                self, possible_coordinate: Tuple[int, int]) -> bool:
            return sum(map(
                        lambda x: x < 0 or x >= BOARD_DIMENSION,
                        possible_coordinate)) == 0

        def alternate_obstacle_at(self, coordinate: Tuple[int, int]) -> None:
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

        def get_node_at(self, coordinate: Tuple[int, int]) -> TNode:
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
            weight = height = self.dimension
            self.grid = [
                [Node(
                    pygame, y, x)
                    for x in range(weight)]
                for y in range(height)]
            self.add_adjacent_neighbours()
            self.add_diagonal_neighbours()

    instance = None

    def __init__(self, pygame, dimension: int) -> None:
        if not Board.instance:
            Board.instance = Board.__Board(pygame, dimension)

    def __getattr__(self, name):
        ''' Encapsules attributes for the singleton '''
        return getattr(self.instance, name)


def euclidean_distance(
        start_coordinate: Tuple[int, int],
        goal_coordinate: Tuple[int, int]) -> float:
    ''' Receives two coordinates (y, x) and return their distance using
    euclidean distance'''
    return (
        (goal_coordinate[0] - start_coordinate[0])**2 +
        (goal_coordinate[1] - start_coordinate[1])**2) ** (1/2)


def manhattan_distance(
        start_coordinate: Tuple[int, int],
        goal_coordinate: Tuple[int, int]) -> int:
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


def upper_confidence_bound(node: TNode) -> float:
    if node.n == 0:
        return float('inf')
    if node.parent_node is None:
        parent_children_count = 0
    else:
        parent_children_count = node.parent_node.n
    ucb1 = node.t/node.n + 2*(
        numpy.log(parent_children_count)/node.n) ** (1/2)
    return ucb1


def draw_board_simulation(simulated_paths: List[List[TNode]]) -> None:
    ''' Show the board if there's already a board created '''
    board = Board(0, 0)

    for path in simulated_paths:
        for node in path:
            if board.start_node != node and\
                    node not in board.goal_nodes:
                node.set_colour(PURPLE_COLOUR)
        board.show()
        sleep(TIME_TICK)


def clear_board_simulation(simulated_paths: List[List[TNode]]) -> None:
    ''' Show the board if there's already a board created '''
    board = Board(0, 0)

    for path in simulated_paths:
        for node in path:
            if board.start_node != node and\
                    node not in board.goal_nodes:
                node.set_colour(WHITE_COLOUR)
        board.show()


def simulation(
        initial_node: TNode, goal_node: TNode) -> float:
    simulated_paths = []
    summation_value = 0
    simulations_count = 0

    for neighbour_node in initial_node.neighbours:
        ''' Starting simulated clone paths'''
        if not neighbour_node.traversable or neighbour_node.n != 0:
            continue
        else:
            simulations_count += 1

        simulated_path = [neighbour_node]
        choosen_node = neighbour_node
        for i in range(10):
            ''' For each path, expand the path randomized'''
            valid_nodes = [
                node for node in choosen_node.neighbours
                if node.n == 0 and node.traversable
                and node not in simulated_path]
            valid_nodes_count = len(valid_nodes)
            if valid_nodes_count == 0:
                break
            random_index = random.randint(0, valid_nodes_count-1)
            choosen_node = valid_nodes[random_index]
            if choosen_node == goal_node:
                return float('inf')
            simulated_path.append(choosen_node)

        last_simulated_node = simulated_path[-1]
        distance_to_object_simulated_value = 1/manhattan_distance(
                last_simulated_node.get_coordinates(),
                goal_node.get_coordinates()) * 100
        summation_value = distance_to_object_simulated_value
        simulated_paths.append(simulated_path)
    draw_board_simulation(simulated_paths)
    clear_board_simulation(simulated_paths)
    if simulations_count == 0:
        average_value = 0
    else:
        average_value = summation_value/simulations_count
    return average_value


def monte_carlo_pathfind(start: TNode, goal: TNode) -> List[TNode]:
    ''' Following Ankit Choudhary instructions available in analyticsvidhya
        Selection
            Selecting good child nodes, starting from the root node R,
            that represent states leading to better overall outcome (win).
        Expansion
            If L is a not a terminal node (i.e. it does not end the game), then create one or more child nodes and select one (C).
        Simulation (rollout)
            Run a simulated playout from C until a result is achieved.
        Backpropagation
            Update the current move sequence with the simulation result.
    '''
    open_set = set()
    closed_set = set()
    start.parent_node = None
    open_set.add(start)
    while(open_set):
        try:
            r_node = max(open_set, key=upper_confidence_bound)
        except AttributeError as e:
            print(open_set)
            exit(1)
        open_set.remove(r_node)
        open_set, found = monte_carlo_search_neighbours(
            r_node, goal, open_set, closed_set)
        if found:
            path = extract_path(goal)
            return path
        closed_set.add(r_node)
    return []


def monte_carlo_search_neighbours(
        root_node, goal, open_set, closed_set):
    '''  Selection
            Selecting good child nodes, starting from the root node R,
            that represent states leading to better overall outcome (win). '''
    print("Nó raiz:", root_node.get_coordinates())
    for i, neighbour in enumerate(root_node.neighbours):
        ''' Expansion
            If L is a not a terminal node (i.e. it does not end the game),
            then create one or more child nodes and select one (C). '''
        print("Vizinho: ", i, " ", neighbour.get_coordinates())
        if neighbour in closed_set or not neighbour.traversable:
            continue

        if neighbour.get_coordinates() == goal.get_coordinates():
            ''' if successor is the goal, stop search '''
            neighbour.add_parent(root_node)
            return open_set, True

        if neighbour.n == 0:
            ''' Simulation (rollout)
            Run a simulated playout from C until a result is achieved. '''
            
            neighbour.t = simulation(neighbour, goal)
            neighbour.n = 1
            neighbour.add_parent(root_node)
            root_node.child_nodes_num_monte_carlo += 1
            print("Atualizando nó filho: ", neighbour.get_coordinates())
            print(
                    "Valor do filho: ", neighbour.t, neighbour.n)
            print("UCB filho: ", upper_confidence_bound(neighbour))
            ''' Backpropagation
            Update the current move sequence with the simulation result. '''
            not_updated_parent = neighbour.parent_node
            while(not_updated_parent):
                print(
                    "Backpropagation nó pai: ",
                    not_updated_parent.get_coordinates())
                not_updated_parent.t += neighbour.t
                not_updated_parent.n += 1
                print(
                    "Valor do pai: ",
                    not_updated_parent.t, not_updated_parent.n)
                not_updated_parent = not_updated_parent.parent_node
            open_set.add(neighbour)
            print()
        elif neighbour not in open_set:
            print("Xablau: ", neighbour.get_coordinates())
            print(neighbour.__dict__)
            print(open_set)
            print(closed_set)
            input()
            open_set.add(neighbour)

    show_board(open_set, closed_set)
    return open_set, False


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
