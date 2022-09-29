# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 16:30:04 2022

@author: Marc Johler
"""

import numpy as np
import utils

class Player:
    def __init__(self, color):
        assert(color in ["red", "green", "blue", "yellow", "black", "white"])
        self.color = color
        # assign partner color
        self.partner = utils.partner(color)
        # remember initial color
        self.initial_color = color
        # initialize hand
        self.hand = np.array([])
        # remember if player has finished
        self.finished = False
        # compute probabilties for cards of other players
        self.card_probabilties = None
        
    def add_to_hand(self, card):
        self.hand = np.append(self.hand, card)
    
    def remove_from_hand(self, card):
        if not card in self.hand:
            raise ValueError("Card is not in players hand")
        pos_card = np.argwhere(self.hand == card)[0]
        self.hand = np.delete(self.hand, pos_card)
            
    def exchange_cards(self, other_player, give, receive):
        self.remove_from_hand(give)
        other_player.add_to_hand(give)
        other_player.remove_from_hand(receive)
        self.add_to_hand(receive)