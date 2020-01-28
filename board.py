import random
from time import sleep
from typing import List, TypeVar

import noise
import pygame

# Colours
WHITE_COLOUR, BLACK_COLOUR = (255, 255, 255), (0, 0, 0)
ORANGE_COLOUR = (255, 165, 0)
GREENYELLOW_COLOUR, POWDERBLUE_COLOUR = (173, 255, 47), (176, 224, 230)
DARKSEAGREEN_COLOUR, DARKGREEN_COLOUR = (143, 188, 143), (0,  100, 0)

# Sizes and Dimensions
CANVAS_DIMENSION = 500
BOARD_DIMENSION = 20
SQUARE_SIZE = int(CANVAS_DIMENSION/BOARD_DIMENSION)
MENU_BAR_HEIGHT = 100
NODE_SIZE = SQUARE_SIZE - 1
OBSTACLES_RATIO = 0.3



# Time
TIME_TICK = 0.01


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
            self.end_node = []
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
                as the start node.
                If other node was already the start, the old
                start node becomes a normal node.'''
            if not self.start_node:
                self.start_node = self.get_node_at(coordinates)
                self.start_node.set_colour(POWDERBLUE_COLOUR)
                self.start_node.set_special(True)
                self.start_node.set_obstacle(False)
            else:
                self.remove_start_node()
                self.start_node = self.get_node_at(coordinates)
                self.start_node.set_colour(POWDERBLUE_COLOUR)
                self.start_node.set_special(True)
                self.start_node.set_obstacle(False)

        def remove_start_node(self) -> None:
            ''' Changes the start node to a normal node again '''
            self.start_node.set_special(False)
            self.start_node.set_colour(WHITE_COLOUR)
            self.start_node = None

        def set_end(self, coordinates: (int, int)) -> None:
            ''' Add the node at given coordinates as an goal node '''
            node = self.get_node_at(coordinates)
            node.set_colour(ORANGE_COLOUR)
            node.set_special(True)
            node.set_obstacle(False)
            self.end_node.append(node)

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
            x_length = len(self.grid)
            y_length = len(self.grid[0])
            base = 0
            for i in range(x_length):
                for j in range(y_length):
                    if (noise.snoise2(
                                i/x_length*3,
                                j/y_length*3,
                                1)+1)/2 < percentual_chance:
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


def double_dijkstras_pathfinding(start: TNode, goal: TNode) -> bool:
    ''' Like normal dijkstra's algorithm, but searching from both
      start and end at same time. Returns true if found a path
      and goal will have a recursive path till start using
      parent_node attribute '''
    if start == goal:
        goal.parent_node = start
        return True

    open_sets = [set() for i in range(2)]
    closed_sets = [set() for i in range(2)]

    open_sets[0].add(start)
    open_sets[1].add(goal)
    while(open_sets[0] and open_sets[1]):
        ''' while any of the open lists are not empty find the nodes
            with the least f on the  each open list, call it "q"'''
        q_nodes = []
        for i in range(2):
            q_nodes.append(min(open_sets[i], key=lambda x: x.f))
            open_sets[i].remove(q_nodes[i])
        ''' pop each q off each open list '''

        open_sets[0], found = dijkstras_search_neighbours(
            q_nodes[0], goal, open_sets[0], closed_sets[0])
        if found:
            return True
        open_sets[1], found = dijkstras_search_neighbours(
            q_nodes[1], start, open_sets[1], closed_sets[1])
        ''' Search neighbours for both end and starting nodes'''
        if found:
            current_node = start
            previous_node = None
            while(current_node):
                next_node = current_node.parent_node
                current_node.parent_node = previous_node
                previous_node = current_node
                current_node = next_node
            return True

        for i in range(2):
            closed_sets[i].add(q_nodes[i])

        if bool(open_sets[0].intersection(open_sets[1])):
            ''' If there's a node that's in both open sets then
                a path was found. Now we need to connect then '''
            intersection_node = min(
                open_sets[0].intersection(open_sets[1]), key=lambda x: x.f)

            if intersection_node.parent_node == q_nodes[0]:
                closest_neighbour = min(
                    closed_sets[1].intersection(intersection_node.neighbours),
                    key=lambda x: x.f)
                current_node = closest_neighbour
            else:
                closest_neighbour = min(
                    closed_sets[0].intersection(intersection_node.neighbours),
                    key=lambda x: x.f)
                current_node = closest_neighbour

            previous_node = intersection_node
            while(current_node):
                next_node = current_node.parent_node
                current_node.parent_node = previous_node
                previous_node = current_node
                current_node = next_node
            return True

        show_board(
            open_sets[0].union(open_sets[1]),
            closed_sets[0].union(closed_sets[1]))

    return False
    ''' If neither the intersection or the goals weren't reached
        then no path can be found '''


def shortest_path_dfs(start, goal):
    ''' Finds the shortest path among all possible paths
        available in the graph. Return True if found
        and the path is available inside the nodes '''
    all_possible_paths = depth_first_search(start, goal)
    if not all_possible_paths:
        return False
    shortest_path = min(all_possible_paths, key=lambda x: len(x))
    previous_node = shortest_path[0]
    for node in shortest_path[1:]:
        node.parent_node = previous_node
        previous_node = node
    return True


def depth_first_search(start, goal):
    ''' Search all paths in the graph looking
        between start and goal using depth first'''
    stack = [(start, [start])]
    all_paths = []
    while stack:
        (vertex, path) = stack.pop()
        for next_node in vertex.neighbours - set(path):
            if next_node == goal:
                all_paths.append(path + [next_node])
            elif next_node.traversable:
                stack.append((next_node, path + [next_node]))
        show_board(set(path), set())
    return all_paths


def shortest_path_bfs(start, goal):
    ''' Finds the shortest path using breath_first_search.
        Return True if found and the path is available
        inside the nodes '''
    shortest_path = breath_first_search(start, goal)
    if not shortest_path:
        return False
    previous_node = shortest_path[0]
    for node in shortest_path[1:]:
        node.parent_node = previous_node
        previous_node = node
    return True


def breath_first_search(start, goal):
    ''' BFS also searches for all paths
        but as first found is the shortest
        returns the first one'''
    queue = [(start, [start])]
    while queue:
        (vertex, path) = queue.pop(0)
        for next in vertex.neighbours - set(path):
            if next == goal:
                return path + [next]
            elif next.traversable:
                queue.append((next, path + [next]))
        show_board(set(path), set())
    return None


def show_board(open_set, closed_list) -> None:
    ''' Show the board if there's already a board created '''
    board = Board(0, 0)
    for node in open_set:
        if board.start_node != node and\
                board.end_node != node:
            node.set_colour(GREENYELLOW_COLOUR)
    for node in closed_list:
        if board.start_node != node and\
                board.end_node != node:
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
        sleep(TIME_TICK*10)
