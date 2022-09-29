# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:11:18 2022

@author: Marc Johler
"""
# set up dictionaries for card values
number_dict = dict([(str(i), [i]) for i in range(2, 11)])
high_card_dict = {"J": ["exchange"], "Q": [12], "K": ["out", 13], "A": ["out", 1, 11], "Joker": ["joker"]}
card_dict = {**number_dict, **high_card_dict}

# function to map color to partner color
def partner(color):
    if color == "red":
        return("blue")
    elif color == "green":
        return("yellow")
    elif color == "blue":
        return("red")
    elif color == "yellow":
        return("green")
    elif color == "black":
        return("white")
    elif color == "white":
        return("black")