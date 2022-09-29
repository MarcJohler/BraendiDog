# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 13:05:00 2022

@author: xZoCk
"""
import numpy as np
from class_card_stack import Card_stack
cs = Card_stack()
prior = cs.prob_to_distribute(4, 6)

own_hand = np.array(["K", "2", "3", "4", "5", "6"])

#def update_prior(prior, cards):
    
    
    