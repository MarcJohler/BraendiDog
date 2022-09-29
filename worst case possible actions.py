# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 17:01:27 2022

@author: Marc Johler
"""
import scipy.special as ss

# for number cards 2, 3, 5, 6, 8 - 10, Q
worst_case_number = 4

# for 4
worst_case_4 = 2 * 4

# for 7 (including order of movement)
# for a maximum of 3 steps it can happen, that there are two possible paths
worst_case_7 = 4 ** 4 * 5 ** 3

# worst case Joker
worst_case_jack = 4 * (4 * 3)

# worst case king
worst_case_king = 2 * 3 + 3 

# worst case ace
worst_case_ace = 3 * 3 + 5

# worst case joker
worst_case_joker = worst_case_number * 8 + worst_case_4 + worst_case_7 + worst_case_jack + worst_case_king + worst_case_ace