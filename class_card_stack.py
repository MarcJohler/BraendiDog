# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 15:00:13 2022

@author: Marc Johler
"""
import numpy as np
import pandas as pd

class Card_stack:
    def __init__(self, n_decks = 2, include_jokers = True):
        numbers = np.repeat(range(2, 11, 1), n_decks * 4)
        high_cards = np.repeat(["J", "Q", "K", "A"], n_decks * 4)
        if include_jokers:
            jokers = np.repeat("Joker", n_decks * 3)
            self.draw_pile = np.concatenate((numbers, high_cards, jokers))
        else:
            self.draw_pile = np.concatenate((numbers, high_cards))
        self.discard_pile = np.array([])
        self.shuffle()
        
    def shuffle(self):
        np.random.shuffle(self.draw_pile)
    
    def distribute(self, n_players, n_cards):
        required_cards = n_players * n_cards
        if required_cards > len(self.draw_pile) + len(self.discard_pile):
            raise ValueError("required number of cards is too high")
        card_diff = required_cards - len(self.draw_pile)
        if card_diff > 0:
            # take all remaining cards from draw pile
            cards_to_distribute = self.draw_pile
            self.draw_pile = self.discard_pile
            self.shuffle()
            # and missing cards from shuffled draw pile
            missing_cards = self.draw_pile[0:card_diff]
            # remove cards from draw pile
            self.draw_pile = np.delete(self.draw_pile, range(0, card_diff))
            # concetanate all cards which shall be distributed
            cards_to_distribute = np.concatenate((cards_to_distribute, missing_cards))
            # put cards on the discard pile
            self.discard_pile = cards_to_distribute
            # return the hands to be distributed
            return np.reshape(cards_to_distribute, (n_players, n_cards))
        # otherwise just draw from the draw pile
        cards_to_distribute = self.draw_pile[0:required_cards]
        self.draw_pile = np.delete(self.draw_pile, range(0, required_cards))
        # put cards on the discard pile
        self.discard_pile = np.concatenate((cards_to_distribute, self.discard_pile))
        # return the hands to be distributed
        return np.reshape(cards_to_distribute, (n_players, n_cards))
    
    def prob_to_distribute(self, n_players, n_cards):
        required_cards = n_players * n_cards
        if required_cards > len(self.draw_pile) + len(self.discard_pile):
            raise ValueError("required number of cards is too high")
        
        # saving information on cards and probabilities
        cards = self.draw_pile
        card_diff = required_cards - len(self.draw_pile)
        if card_diff > 0:
            # cards in draw pile
            probabilities = np.ones(len(self.draw_pile))
            # cards in discard pile
            prob_remaining_cards = card_diff / len(self.discard_pile)
            cards = np.append(cards, self.discard_pile)
            probabilities = np.append(probabilities, np.repeat(prob_remaining_cards, len(self.discard_pile)))
        else:
            prob_per_card = required_cards / len(self.draw_pile)
            probabilities = np.repeat(prob_per_card, len(self.draw_pile))
        
        prob_dict = {"card": cards, "probability": probabilities}
        return pd.DataFrame.from_dict(prob_dict)