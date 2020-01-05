''' Main module of the pathfinding project. 
Used to show graphic interface.
'''
import pygame

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

        def show(self):
            ''' Prints all board squares on canvas '''
            for column in self.grid:
                for square in column:
                    square.show()
            pygame.display.update()

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
        self.x_coordinate, self.y_coordinate = x_coordinate, y_coordinate
        self.colour = (255, 255, 255)

    def show(self) -> None:
        ''' Draws the square on the board with a little border'''
        self.pygame.draw.rect(
            pygame.display.get_surface(),
            self.colour,
            self.pygame.Rect(
                self.x_coordinate*(SQUARE_SIZE+1),
                self.y_coordinate*(SQUARE_SIZE+1),
                SQUARE_SIZE, SQUARE_SIZE))




pygame_window = pygame.display.set_mode((CANVAS_DIMENSION, CANVAS_DIMENSION))

board = Board(pygame, BOARD_DIMENSION)
board.show()

pygame.quit()
