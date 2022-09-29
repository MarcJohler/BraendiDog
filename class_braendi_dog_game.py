# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 20:01:58 2022

@author: Marc Johler
"""
import numpy as np
import tkinter as tk
import sys
import pandas as pd
import utils
from class_braendi_dog_board import Braendi_Dog_board
from class_card_stack import Card_stack
from class_player import Player

# create root windows for tkinter
ROOT = tk.Tk()
ROOT.withdraw()

class Braendi_Dog:
    def __init__(self, n_players = 4, n_decks = 2, include_jokers = True):
        # remember number of players
        self.n_players = n_players
        # initialize colors
        if n_players == 4:
            self.colors = ["red", "green", "blue", "yellow"]
        elif n_players == 6:
            self.colors = ["red", "green", "blue", "yellow", "black", "white"]
        # initialize board
        self.board = Braendi_Dog_board(n_players)
        # initialize card stack
        self.cards = Card_stack(n_decks, include_jokers)
        # initialize players
        self.players = np.array([])
        for i in range(n_players):
            color = self.colors[i]
            self.players = np.append(self.players, Player(color))
        # iniitialize round counter
        self.round_count = 0
        # randomly decide starting player
        self.starting_player = np.random.choice(range(n_players))
    
    def check_seven_playable(self, player_id):
        current_player = self.players[player_id]
        color = current_player.color
        # check if there is a marble on the start field,
        # if yes that marble can definitely move
        occupied_bool = np.array(self.board.graph_data["occupied"] == color)
        isStart_bool = np.array(self.board.graph_data["isStart"])
        if sum(occupied_bool * isStart_bool) == 1:
            return True
        # otherwise if all marbles are either in goal or kennel, it is not possible to use a 7
        isGoal_bool = np.array(self.board.graph_data["isGoal"])
        isKennel_bool = np.array(self.board.graph_data["isKennel"])
        if sum(occupied_bool * (isGoal_bool + isKennel_bool)) == 4:
            return False
        # otherwise compute sum of steps one can go with all marbles
        marbles_not_finished = np.argwhere(occupied_bool * ~isKennel_bool * ~isGoal_bool)
        steps_covered = 0
        for i in range(len(marbles_not_finished)):
            # save old state in order to be able to restore it later
            old_state = self.board.graph_data.copy(deep = True)
            # information on marble 
            marble_id = marbles_not_finished[i][0]
            label_i = list(self.board.graph_data["label"][marble_id])[0]
            remaining_steps = 7 - steps_covered
            for step in range(remaining_steps):
                try:
                    # check if one step with the marble is possible
                    self.board.move_forwards(color, label_i, 1, enter_goal = 0, plot = False)
                    steps_covered = steps_covered + 1
                except:
                    # otherwise break for-loop
                    break
            # restore old state of the board
            self.board.graph_data = old_state
        
        # check if all steps have been used
        if steps_covered == 7:
            return True
    
        # if steps of these marbles were not sufficient try using marbles in goal area too
        marbles_finished = np.argwhere(occupied_bool * isGoal_bool)
        # assuming higher id = further inside goal area 
        marbles_finished = np.sort(marbles_finished)
        # remember old state 
        old_state = self.board.graph_data.copy(deep = True)
        # check descending to avoid blocking marbles
        for i in reversed(range(len(marbles_finished))):
            # information on marble 
            marble_id = marbles_finished[i]
            label_i = list(self.board.graph_data["label"][marble_id])[0]
            while True:
                try:
                    # check if one step with the marble is possible
                    self.board.move_forwards(color, label_i, 1, plot = False)
                    steps_covered = steps_covered + 1
                except:
                    # otherwise break while-loop
                    break
        # restore old state of the board
        self.board.graph_data = old_state
        
        # if all steps have been used return True
        if steps_covered >= 7:
            return True
        
        # otherwise it is not possible
        return False
        
    def check_movement_possible(self, player_id, steps):
        current_player = self.players[player_id]
        color = current_player.color
        # is card a "4"?
        card_is_4 = steps in ["4", 4]
        # try all possible movements
        all_labels = ["A", "B", "C", "D"]
        # remember variables in lists
        label = np.array([])
        action = np.array([])
        isPossible = np.array([])
        for i in range(len(all_labels)):
            # save old state in order to be able to restore it later
            old_state = self.board.graph_data.copy(deep = True)
            label = np.append(label, all_labels[i])
            action = np.append(action, int(steps))
            try:
                self.board.move_forwards(color, all_labels[i], int(steps), enter_goal = 0, plot = False)
                isPossible = np.append(isPossible, True)
            except:
                isPossible = np.append(isPossible, False)
            # restore old state of the board
            self.board.graph_data = old_state
            # if card is a "4" extra check backwards direction
            if card_is_4:
                # save old state in order to be able to restore it later
                old_state = self.board.graph_data.copy(deep = True)
                label = np.append(label, all_labels[i])
                action = np.append(action, int(steps) * (-1))
                try:
                    self.board.move_backwards(color, all_labels[i], plot = False)
                    isPossible = np.append(isPossible, True)
                except:
                    isPossible = np.append(isPossible, False)
                # restore old state of the board
                self.board.graph_data = old_state
        
        # split the fucking list
        action_dict = {"label": label, "action": action, "isPossible": isPossible}
        # return dataframe with info on actions
        action_data = pd.DataFrame.from_dict(action_dict)
        action_data["action"] = pd.to_numeric(action_data["action"], downcast = "integer")
        action_data["isPossible"] = action_data["isPossible"].astype("bool")
        
        return action_data

    def check_exchanging_possible(self, player_id):
        current_player = self.players[player_id]
        color = current_player.color
        # try all possible movements
        all_labels = ["A", "B", "C", "D"]
        other_colors = np.setdiff1d(self.colors, color)
        # remember variables in lists
        own_label = list(np.repeat(all_labels, (self.n_players - 1) * 4))
        other_color = list(np.repeat(other_colors, 4)) * 4 
        other_label = all_labels * (self.n_players - 1) * 4
        isPossible = [True] * (self.n_players - 1) * 16
        # set up variables which are used multiple times
        occupied_bool = self.board.graph_data["occupied"] == color
        for i in range(len(all_labels)):
            label_i = all_labels[i]
            label_bool = self.board.graph_data["label"] == label_i
            # compute position of own marble
            own_position = int(np.argwhere(np.array(occupied_bool * label_bool)))
            # check if exchange is possible
            try:
                self.board.exchangeable(own_position)
            except:
                # generate indizes which need to be adapted
                indizes = slice(i * (self.n_players - 1) * 4, 
                                (i + 1) * (self.n_players - 1) * 4, 
                                1)
                isPossible[indizes] = np.repeat(False, (self.n_players - 1) * 4)
            # now check for the other marbles
            for j in range(len(other_colors)):
                color_j = other_colors[j]
                # which field are occupied by marbles with color_j?
                occupied_j_bool = self.board.graph_data["occupied"] == color_j
                # compute position of other marble
                other_position = int(np.argwhere(np.array(occupied_j_bool * label_bool)))
                # check if exchange is possible
                try:
                    self.board.exchangeable(other_position)
                except:
                    # generate indizes which need to be adapted
                    indizes = slice(j * 4 + i, 
                                    3 * (self.n_players - 1) * 4 + j * 4 + i + 1, 
                                    (self.n_players - 1) * 4)
                    isPossible[indizes] = np.repeat(False, 4)
                
        exchangable_dict = {"own_label": own_label, 
                            "other_color": other_color,
                            "other_label": other_label,
                            "isPossible": isPossible}
        return pd.DataFrame.from_dict(exchangable_dict)

    def check_playable_cards(self, player_id):
        # identify current player and her hand
        current_player = self.players[player_id]
        player_hand = current_player.hand
        # helper function to delete cards from player_hand
        def delete_if_not_playable(check1, check2 = True):
            if check1 and check2:
                delete_indizes = np.argwhere(player_hand == card)
                return np.delete(player_hand, delete_indizes) 
            return player_hand
        # loop over the cards and check if they can be played
        for card in player_hand:
            check1 = False
            check2 = True
            if card == "Joker":
                continue
            elif card == "7":
                check1 = not self.check_seven_playable(player_id)
            elif card == "J":
                check1 = sum(self.check_exchanging_possible(player_id)["isPossible"]) == 0
            elif card == "K":
                # first check if getting out is possible otherwise check if 13 is possible
                old_state = self.board.graph_data.copy(deep = True)
                try:
                    self.board.out(current_player.color, plot = False)
                    self.board.graph_data = old_state
                except:
                    check1 = sum(self.check_movement_possible(player_id, 13)["isPossible"]) == 0
            elif card == "A":
                # first check if getting out is possible otherwise check if 1 or 11 is possible
                old_state = self.board.graph_data.copy(deep = True)
                try:
                    self.board.out(current_player.color, plot = False)
                    self.board.graph_data = old_state
                except:
                    check1 = sum(self.check_movement_possible(player_id, 1)["isPossible"]) == 0
                    check2 = sum(self.check_movement_possible(player_id, 11)["isPossible"]) == 0
            elif card == "Q":
                check1 = sum(self.check_movement_possible(player_id, 12)["isPossible"]) == 0
            else:
                check1 = sum(self.check_movement_possible(player_id, card)["isPossible"]) == 0
            # delete card from hand if it cannot be played
            player_hand = delete_if_not_playable(check1, check2)
        # return remaining playable cards
        return player_hand
    
    def check_usable_actions(self, player_id, card):
        #identify current player and her hand
        current_player = self.players[player_id]
        usable_actions = np.array([])
        # helper function determine possible actions
        def moving_possible(steps):
            if sum(self.check_movement_possible(player_id, steps)["isPossible"]) != 0:
                return np.append(usable_actions, str(steps))
            return usable_actions
        # check if specific actions are possible
        if card in ["A", "K"]:
            # first check if getting out is possible otherwise check if 13 is possible
            old_state = self.board.graph_data.copy(deep = True)
            try:
                self.board.out(current_player.color, plot = False)
                self.board.graph_data = old_state
                usable_actions = np.append(usable_actions, "out")
            except:
                pass
        if card == "K":
            usable_actions = moving_possible(13)
        elif card == "A":
            usable_actions = moving_possible(1)
            usable_actions = moving_possible(11)
        elif card == "Q":
            usable_actions = moving_possible(12)
        elif card == "J":
            if sum(self.check_exchanging_possible(player_id)["isPossible"]) != 0:
                usable_actions = np.append(usable_actions, "exchange")
        elif card == "7" and self.check_seven_playable(player_id):
            usable_actions = np.append(usable_actions, "7")
        else:
            usable_actions = moving_possible(card)
        
        return usable_actions

    def check_chooseable_cards(self, player_id):
        # last card is joker
        other_cards = np.delete(list(utils.card_dict.keys()), -1)
        chooseable_cards = np.array([])
        for card in other_cards:
            usable_actions = self.check_usable_actions(player_id, card)
            if len(usable_actions) > 0:
                chooseable_cards = np.append(chooseable_cards, card)
        return chooseable_cards
    
    def check_moveable_marbles(self, player_id, steps):
        # check for which marbles movement is possible
        all_options = self.check_movement_possible(player_id, steps)
        possible_options = all_options[all_options["isPossible"]]
        return np.unique(possible_options["label"])
    
    def check_exchangeable_marbles(self, player_id):
        # check for which marbles exchanging is possible
        all_options = self.check_exchanging_possible(player_id)
        possible_options = all_options[all_options["isPossible"]]
        own_marbles = np.unique(possible_options["own_label"])
        # extract relevant data
        other_color = list(possible_options["other_color"])
        other_label = list(possible_options["other_label"])
        # save color-label-pairs as tupels to identify other marbles
        other_marbles = [(other_color[i], other_label[i]) for i in range(len(possible_options))]
        # return both lists
        return [own_marbles, other_marbles]

    def check_possible_directions(self, player_id, label):
        # check for which marbles which directions are possible
        movement_possible = self.check_movement_possible(player_id, 4)
        # extract relevant information
        isPossible = np.array(movement_possible["isPossible"])
        correct_label = np.array(movement_possible["label"] == label)
        relevant_indizes = np.argwhere(isPossible * correct_label)
        # convert it to list of integers
        possible_actions = [movement_possible["action"][int(index)] for index in relevant_indizes]
        # return the corresponding values
        possible_directions = np.array([])
        if 4 in possible_actions:
            possible_directions = np.append(possible_directions, "f")
        if -4 in possible_actions:
            possible_directions = np.append(possible_directions, "b")
        return possible_directions 
        
    def select_card(self, current_player, possible_cards, action):
        # ask current player which card (s)he wants to play
        dialog_message = "Player " + current_player.initial_color + ": which card do you want to " + action + "? \n \n Your hand: "
        
        # show user cards in his/her hand
        for i in range(len(current_player.hand)):
            dialog_message = dialog_message + "\n" + str(current_player.hand[i])
        
        if action != "exchange":
            # additionally show which cards are playable in this turn
            dialog_message = dialog_message + "\n \n Playable: "
            
            for i in range(len(possible_cards)):
                dialog_message = dialog_message + "\n" + str(possible_cards[i])
            
        # select a card via message window
        chosen_card = "nothing chosen"
        while chosen_card not in possible_cards and chosen_card not in ["Joker", "abort", "end game"]:
            chosen_card = tk.simpledialog.askstring(title='Choose card', prompt=dialog_message)
        return(chosen_card)
    
    def select_action(self, current_player, possible_actions):
        # if there is only one possible action, skip asking the player
        if len(possible_actions) == 1:
            return(possible_actions[0])
        # ask current player which actions she wants to use
        dialog_message = "Player " + current_player.initial_color + ": which action do you want to use? \n \n Possible options: "
        
        for i in range(len(possible_actions)):
            dialog_message = dialog_message + "\n" + str(possible_actions[i])
            
        # select a card via message window
        chosen_action = "nothing chosen"
        while chosen_action not in possible_actions and chosen_action not in ["abort", "end game"]:
            chosen_action  = tk.simpledialog.askstring(title='Choose action', prompt=dialog_message)
        return(chosen_action)

    def select_marble(self, current_player, possible_marbles, action, marble = "own"):
        # ask current player which marbles she wants to use
        if marble == "own":
            if action == "move":
                options = possible_marbles
            elif action == "exchange":
                options = possible_marbles[0]
            # if there is only one option automatically choose this one
            if len(options) == 1:
                return options[0]
            # othwerise ask the player which marble (s)he wants to use
            dialog_message = "Player " + current_player.initial_color + ": which marble do you want to " + action + "? \n \n Possible options: "
            for i in range(len(options)):
                dialog_message = dialog_message + "\n" + str(options[i])
        elif marble == "other":
            options = [str(i) for i in range(len(possible_marbles[1]))]
            # if there is only one option automatically choose this one
            if len(options) == 1:
                return options[0]
            # othwerise ask the player which marble (s)he wants to exchange with
            dialog_message = "Player " + current_player.initial_color + ": with which other marble do you want to exchange? \n \n Possible options (select a number): "
            for i in range(len(possible_marbles[1])):
                dialog_message = dialog_message + "\n" + str(i) + ": " + str(possible_marbles[1][i])
        # select a card via message window
        chosen_marble = "nothing chosen"
        while chosen_marble not in options and chosen_marble not in ["abort", "end game"]:
            chosen_marble = tk.simpledialog.askstring(title='Choose card', prompt=dialog_message)
        return chosen_marble
    
    def select_direction(self, current_player, possible_directions):
        # if there is only one possibility skip asking the player
        if len(possible_directions) == 1:
            return(possible_directions[0])
        direction = "nothing chosen"
        dialog_message = "Player " + current_player.initial_color + ": Wanna go forwards or backwards?"
        while direction not in possible_directions:
            direction = tk.simpledialog.askstring(title="Action", prompt = dialog_message)
            if direction in ["forwards", "Forwards", "FORWARDS", "f", "F"]:
                direction = "f"
            elif direction in ["backwards", "Backwards", "BACKWARDS", "b", "B"]:
                direction = "b"
            else:
                direction = "nothing chosen" 
        return direction
        
    def inform_active_player(self, current_player, action):
        # generate dialog_message
        dialog_message = "Player " + current_player.initial_color + ": choose a card to "
        if action == "exchange":
            dialog_message = dialog_message + "exchange with your partner"
        elif action == "play":
            dialog_message = dialog_message + "play this turn"
        
        # confirm via message window
        tk.messagebox.showinfo(title="Turn info", message=dialog_message)
    
    def no_cards_left(self, current_player):
        # generate dialog message
        dialog_message = "Player " + current_player.initial_color + " has no playable cards left"
        # confirm via message window
        tk.messagebox.showinfo(title="Turn info", message=dialog_message)
        
    def turn(self, player_id):
        current_player = self.players[player_id]
        playable_cards = self.check_playable_cards(player_id)
        # stop if there are no more cards left on the players hand
        if len(playable_cards) == 0:
            self.no_cards_left(current_player)
            self.current_order =  self.current_order[~np.in1d(self.current_order, player_id)]
            return
        # otherwise inform player about her turn
        self.inform_active_player(current_player, "play")
            
        # initialize variables for execution of action
        label1 = None
        color2 = None
        label2 = None
        direction  = None
        
        action_executed = False
        while not action_executed:
            # select one card out of all playable cards
            playable_cards = self.check_playable_cards(player_id)
            # check if there are any playable_cards on the hand
            if len(playable_cards) == 0:
                action_executed = True
                self.players[player_id].hand = np.array([])
                self.current_order = self.current_order[~np.in1d(self.current_order, player_id)]
                continue
            chosen_card = self.select_card(current_player, playable_cards, "play")
            if chosen_card in ["abort", "end game"]:
                sys.exit("A player has ended the game")
            # if Joker has been chosen replace the Joker with the card you want to use
            if chosen_card == "Joker":
                chooseable_cards = self.check_chooseable_cards(player_id)
                use_card_as = self.select_card(current_player, chooseable_cards, "use the joker for")
                if  use_card_as in ["abort", "end game"]:
                    sys.exit("A player has ended the game")
            else:
                use_card_as = chosen_card
            # if there is only one action use it, otherwise ask the player which action to use
            possible_actions = self.check_usable_actions(player_id, use_card_as)
            chosen_action = self.select_action(current_player, possible_actions)
            if chosen_action in ["abort", "end game"]:
                sys.exit("A player has ended the game")
            # according to what action has been chosen do the following:
            if chosen_action == "out":
                pass
            elif chosen_action == "exchange":
                exchangeable_marbles = self.check_exchangeable_marbles(player_id)
                label1 = self.select_marble(current_player, exchangeable_marbles, "exchange", marble = "own")
                other_marble = int(self.select_marble(current_player, exchangeable_marbles, "exchange", marble = "other"))
                color2 = exchangeable_marbles[1][other_marble][0]
                label2 = exchangeable_marbles[1][other_marble][1]
            elif chosen_action == "7":
                # if there is only one marble moveable, apply action automatically
                moveable_marbles = self.check_moveable_marbles(player_id, 1)
                if len(moveable_marbles) == 1:
                    label1 = moveable_marbles[0]
            else:
                moveable_marbles = self.check_moveable_marbles(player_id, chosen_action)
                # if there is only one moveable marble, simply choose it, otherwise ask the player
                label1 = self.select_marble(current_player, moveable_marbles, "move", marble = "own")
            
            # ask which direction if a 4 has been played
            if chosen_action == "4":
                possible_directions = self.check_possible_directions(player_id, label1)
                direction = self.select_direction(current_player, possible_directions)
            
            action_executed = True

            # workaround for finishing both colors with seven
            seven_finished = self.board.execute_action(chosen_action, current_player.color, label1, color2, label2, direction)
            self.players[player_id].remove_from_hand(chosen_card)
        # check if player has finished
        player_color = current_player.color
        if self.board.check_finished(player_color):
            # check if partner is finished or own color is already finished 
            partner_id = int((player_id + self.n_players / 2) % self.n_players)
            partner = self.players[partner_id]
            if partner.finished or current_player.finished or seven_finished:
                # dialog for winning team
                dialog_message = "Congratuliations! Player " + current_player.initial_color + " and " + partner.initial_color + " have won the game!"
                tk.messagebox.showinfo(title="Game end", message=dialog_message)
                sys.exit()
            # otherwise remember that player is finished ... 
            self.players[player_id].finished = True
            # ... and change the color of the active player
            self.players[player_id].color = partner.color
                
    def rounds(self):
        self.round_count = self.round_count + 1
        dialog_message = "Round number " + str(self.round_count)
        tk.messagebox.showinfo(title="New round", message=dialog_message)
        current_order = np.repeat(None, self.n_players)
        for i in range(self.n_players):
            current_order[i] = (self.starting_player + i) % self.n_players
        self.current_order = current_order
        
        # distribute cards
        n_cards = 6 - (self.round_count - 1) % 5 
        hands = self.cards.distribute(self.n_players, n_cards)
        
        # distribute cards and exchange cards between team mates
        exchange_cards = np.repeat(None, self.n_players)
        for i in range(self.n_players):
            # extract relevant information
            current_player_id = self.current_order[i]
            current_player = self.players[current_player_id]
            player_hand = hands[i]
            # save hand in player object
            self.players[current_player_id].hand = player_hand
            # inform player of her turn 
            self.inform_active_player(current_player, "exchange")
            chosen_card = "replaceme"
            while chosen_card not in player_hand and chosen_card != "abort":
                chosen_card = self.select_card(current_player, player_hand, "exchange")
            if chosen_card == "abort":
                sys.exit("A player stopped the game")
            exchange_cards[i] = chosen_card
        
        # do the exchanges
        for i in range(int(self.n_players / 2)):
            first_player_id = self.current_order[i]
            first_player = self.players[first_player_id]
            j = int(i + self.n_players / 2)
            second_player_id = self.current_order[j]
            second_player = self.players[second_player_id]
            first_player.exchange_cards(second_player, 
                                        exchange_cards[i], 
                                        exchange_cards[j])
        # do turns
        i = 0
        while len(self.current_order) > 0:
            players_in_game = len(self.current_order)
            # let player do her turn
            self.turn(self.current_order[i])
            #  set new index with this formula to avoid if-statement
            still_in_game = players_in_game == len(self.current_order)
            # check if there are any players left
            players_in_game_new = players_in_game - 1 + still_in_game
            # if no players left terminate the round
            if players_in_game_new == 0:
                break
            # otherwise update the active player
            i = (i + still_in_game) % players_in_game_new
        
        # set new starting player
        self.starting_player = (self.starting_player + 1) % self.n_players 
    
    def start_game(self):
        # ask if player wants to start the game
        if not tk.messagebox.askyesno("Braendi Dog","Do you want to start the game?"):
            sys.exit()
        # plot the board visualisation
        self.board.plot()
        while True:
            self.rounds()
          
        