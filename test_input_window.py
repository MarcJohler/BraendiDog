# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 13:45:34 2022RO

@author: xZoCk
"""

from class_braendi_dog_board import Braendi_dog_board

board = Braendi_dog_board(4)
board.plot()

board.out("yellow")
board.move_forward(62, "yellow", "A")
board.out("blue")
board.move_forward(15, "blue", "A")
board.out("yellow")
board.move_forward(11, "yellow", "B")
board.out("yellow")

board.execute_action("Joker", "yellow")