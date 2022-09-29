# -*- coding: utf-8 -*-
"""
Created on Sun Feb 27 13:35:06 2022

@author: Marc Johler
"""
from class_braendi_dog_board import Braendi_dog_board

board = Braendi_dog_board(4)
board.plot()

# must work
board.out("blue")
# must work
board.move_forward(10, "blue", "A")
# must work
board.out("yellow")
# must throw error
board.move_forward(10, "blue", "A")
# must work
board.move_forward(3, "blue", "A")
# must work
board.move_forward(10, "yellow", "A")
# must work
board.move_forward(10, "blue", "A")
# must work
board.move_forward(6, "blue", "A")
# must throw error
board.move_forward(10, "yellow", "A")
# must work
board.move_forward(6, "blue", "A")
board.out("red")
# must throw error
board.forward("red")
# must work
board.move_forward(6, "red", "A")
board.out("red")
board.move_forward(5, "red", "B")
board.out("red")
board.move_forward(4, "red", "C")
board.out("red")
# must throw error
board.out("red")
# must throw error
board.move_forward(4, "red", "D")
# must work
board.move_forward(3, "red", "D")
board.out("red")



