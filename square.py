import pygame
from gui_helper import WHITE_COLOUR, SQUARE_SIZE
from typing import TypeVar

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
