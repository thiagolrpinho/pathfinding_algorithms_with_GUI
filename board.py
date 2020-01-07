from square import Square, TSquare
import pygame
from gui_helper import BOARD_DIMENSION, POWDERBLUE_COLOUR,\
    ORANGE_COLOUR, GREENYELLOW_COLOUR, DARKSEAGREEN_COLOUR, TIME_TICK
from time import sleep
import random


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
            ''' Configure the square at given coordinates as the start square '''
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
                open_list, found = self.a_star_search_neighbours(
                    q_node, goal, open_list, closed_list)
                if found is True:
                    return True
                closed_list.append(q_node)
            return False

        def a_star_search_neighbours(
                self, q_node, goal, open_list, closed_list):
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
                temp_g = q_node.g + self.distance_between(q_node, neighbour)
                if neighbour in open_list:
                    neighbour_index = open_list.index(neighbour)
                    if temp_g > open_list[neighbour_index].g:
                        continue
                neighbour.g = temp_g
                neighbour.add_parent(q_node)
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
                sleep(TIME_TICK)
            return open_list, False

        def get_square_at(self, coordinate: (int, int)) -> TSquare:
            ''' Returns the square available at given coordinate if it exists'''
            square = None
            if self.is_valid_coordinate(coordinate):
                square = self.grid[coordinate[0]][coordinate[1]]
            else:
                square = None
            return square

        def euclidean_distance(
                self,
                start_coordinate: (int, int),
                goal_coordinate: (int, int)) -> float:
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
