# -*- coding: utf-8 -*-
"""
Created on Sun Feb 27 13:34:13 2022

@author: Marc Johler
"""
import math
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import warnings
import tkinter as tk
import utils

# create root windows for tkinter
ROOT = tk.Tk()
ROOT.withdraw()

class Braendi_Dog_board:
    def __init__(self, n_players):
        if n_players == 4:
            # red - green - blue - yellow
            graph_data = pd.read_csv("2VS2_grid.csv", sep = ";")
            self.n_nodes = len(graph_data)
            graph_data = graph_data.assign(protected = np.repeat(False, self.n_nodes))
            self.graph_data = graph_data
            
            # generate dictionary for node positions
            positions = [[graph_data['x'][i], graph_data['y'][i]] for i in range(self.n_nodes)]
            self.position_data = dict([[graph_data['id'][i], positions[i]] for i in range(self.n_nodes)])
            
            # node attribute data as dictionary
            node_data = graph_data[["isStart", "isGoal", "isKennel", "color", "occupied", "label", "protected"]].to_dict(orient = "index")
            
            # create ludo board
            board = nx.DiGraph()
            
            # add nodes + attributes
            board.add_nodes_from(node_data)
            nx.set_node_attributes(board, node_data)
            
            edges = nx.from_pandas_edgelist(graph_data,
                                            source = 'predecessor',
                                            target = 'id',
                                            create_using = nx.DiGraph)
            board.add_edges_from(edges.edges)
            # save board state 
            self.board_graph = board
            # variable for remember old state
            self.state_history = []
            # remember if players have all their marbles in goal area
            self.finished = np.repeat(False, n_players)
    
    # define function to check if marbles are exchangeable
    def exchangeable(self, position):
        isKennel_bool = self.graph_data["isKennel"][position] 
        isStart_bool = self.graph_data["isStart"][position]
        protected_bool = self.graph_data["protected"][position]
        if isKennel_bool:
            raise ValueError("At least one of the marbles is not out of the home area yet")
        if protected_bool and isStart_bool:
            raise ValueError("At least one of the marbles is still in protected state")
        if protected_bool:
            raise ValueError("At least one of the marbles is already in the goal area")
    
    def check_finished(self, color):
        isGoal_bool = self.graph_data["isGoal"]
        occupied_bool = self.graph_data["occupied"] == color
        
        # if all marbles are in the goal area return True, False otherwise
        if sum(isGoal_bool * occupied_bool) == 4:
            return(True)
        
        return(False)
    
    def kick(self, color, label):
        free_bool = np.array(self.graph_data["occupied"] != color)
        color_bool = np.array(self.graph_data["color"] == color)
        isKennel_bool = np.array(self.graph_data["isKennel"])
        
        new_pos = int(np.argwhere(color_bool * isKennel_bool * free_bool)[0])
        # set the marble to a free field in the start area
        self.graph_data["occupied"][new_pos] = color
        self.graph_data["label"][new_pos] = label
    
    def out(self, color, plot = True):
        # temporarily turn off warnings
        warnings.filterwarnings("ignore")
    
        color_bool = np.array(self.graph_data["color"] == color)
        start_bool = np.array(self.graph_data["isStart"])
        # check if start field is free
        start_field = int(np.argwhere(color_bool * start_bool))
        if self.graph_data["protected"][start_field]: 
            raise ValueError("Start field is blocked! Cannot place marble on the board")
            
        isKennel_bool = np.array(self.graph_data["isKennel"])
        occupied_bool = np.array(self.graph_data["occupied"] == color)
        marble_position = np.argwhere(color_bool * isKennel_bool * occupied_bool)
        if len(marble_position) == 0:
            raise ValueError("No more marbles left in start area")
        marble_position = int(marble_position[0])
        
        ## otherwise assume it's a valid move and place marble on start field
        # if there is a marble of another color on the start field kick it
        kicked_color = self.graph_data["occupied"][start_field]
        kicked_label = self.graph_data["label"][start_field]
        if kicked_color != 'False':
            self.kick(kicked_color, kicked_label)
        # place marble on the start field        
        self.graph_data["occupied"][start_field] = color
        self.graph_data["label"][start_field] = self.graph_data["label"][marble_position]
        self.graph_data["protected"][start_field] = True
        # and remove it from home area
        self.graph_data["occupied"][marble_position] = "False"
        self.graph_data["label"][marble_position] = math.nan
        
        # turn on warnings again
        warnings.filterwarnings("default")
        
        # plot new board
        if plot:
            self.plot()
    
    def move_forwards(self, color, label, steps, enter_goal = "decide", plot = True):
        # temporarily turn off warnings
        warnings.filterwarnings("ignore")
        occupied_bool = np.array(self.graph_data["occupied"] == color)
        label_bool = np.array(self.graph_data["label"] == label)
        marble_position = int(np.argwhere(occupied_bool * label_bool))
        
        if self.graph_data["isKennel"][marble_position]:
            raise ValueError("Marble is not out of the home area yet")
        
        just_started = self.graph_data["protected"][marble_position]
        new_position = marble_position
        # remember if moved into goal
        entered_goal = False
        for i in range(steps):
            new_position = [s for s in self.board_graph.successors(new_position)]
            n_candidates = len(new_position)
            # check if already reached last field:
            if n_candidates == 0:
                raise ValueError("no more moves with this marble possible")
            # it could be that marble is trying to pass a protected field
            if n_candidates == 1:
                if self.graph_data["protected"][new_position[0]]:
                    raise ValueError("way is blocked by another marble!")
            # exclude irrelevant directions
            elif n_candidates > 1:
                for j in reversed(range(n_candidates)):
                    candidate_j = new_position[j]
                    isGoal_j = self.graph_data["isGoal"][candidate_j]
                    # check if candidate is start of goal area
                    if isGoal_j: 
                        color_j = self.graph_data["color"][candidate_j]
                        # discard possibility if it's a foreign goal area or the
                        # marble was moved out of the home area with its last action
                        if color_j != color or just_started:
                            new_position = np.delete(new_position, j)
                        elif self.graph_data["occupied"][candidate_j] == color:
                            new_position = np.delete(new_position, j)
                        else:
                            # otherwise check if goal area can be entered
                            remaining_fields = 1
                            next_field = candidate_j
                            for k in range(3):
                                next_field = [s for s in self.board_graph.successors(next_field)][0]
                                field_occupied = self.graph_data["occupied"][next_field] == color
                                if field_occupied:
                                    break
                                remaining_fields = remaining_fields + 1
                            # check if number of remaining steps in goal area is sufficient
                            # and discard option if not
                            if remaining_fields < steps - i:
                                new_position = np.delete(new_position, j)
                                
            # if there are still two options, let the user decide
            if len(new_position) > 1:
                while enter_goal == "decide":
                    enter_goal = tk.simpledialog.askstring(title="Move forwards", prompt="Wanna enter goal area?")
                    if enter_goal in ["yes", "y", "Yes", "Y", "YES", "True", "true", "TRUE", "t", "T", "1"]:
                        enter_goal = 1
                        entered_goal = True
                    elif enter_goal in ["no", "n", "No", "N", "NO", "False", "false", "FALSE", "f", "F", "0"]:
                        enter_goal = 0
                    else:
                        enter_goal = "decide"
                new_position = new_position[enter_goal]
            else:
                new_position = new_position[0]
        
        # it could be that marble is landing on a protected field
        if self.graph_data["protected"][new_position]:
            raise ValueError("way is blocked by another marble!")
        
        # final check for position to be free and kick other marble if possible
        kicked_color = self.graph_data["occupied"][new_position]
        if kicked_color != 'False':
            kicked_label = self.graph_data["label"][new_position]
            # set the marble to a free field in the start area
            self.kick(kicked_color, kicked_label)
        
        # put marble on the new spot
        self.graph_data["occupied"][new_position] = color
        self.graph_data["label"][new_position] = label
        # also make marble unpassable if it entered goal_area
        if self.graph_data["isGoal"][marble_position] or entered_goal:
            self.graph_data["protected"][new_position] = True
        
        # delete marble from old position
        self.graph_data["occupied"][marble_position] = "False"
        self.graph_data["label"][marble_position] = math.nan
        self.graph_data["protected"][marble_position] = False
        
        # turn on warnings again
        warnings.filterwarnings("default")
        
        # plot new board
        if plot:
            self.plot()
    
    def single_steps(self, color, label, steps, plot = True):
        for i in range(steps):
            self.move_forwards(color, label, 1, plot = False) 
        # plot new board
        if plot:
            self.plot()
    
    def check_steps_possible(self, color, label, max_steps = 7):
        old_state = self.graph_data.copy(deep = True)
        no_steps_possible = 0
        for i in range(max_steps):
            try:
                self.move_forwards(color, label, 1, enter_goal = False, plot = False)
                no_steps_possible = no_steps_possible + 1
            except:
                break
        self.graph_data = old_state
        return no_steps_possible
        
    def move_backwards(self, color, label, plot = True):
        # temporarily turn off warnings
        warnings.filterwarnings("ignore")
        occupied_bool = np.array(self.graph_data["occupied"] == color)
        label_bool = np.array(self.graph_data["label"] == label)
        marble_position = int(np.argwhere(occupied_bool * label_bool))
        
        if self.graph_data["isKennel"][marble_position]:
            raise ValueError("Marble is not out of the home area yet")
            
        # check if marble is already in goal
        if self.graph_data["isGoal"][marble_position]:
            raise ValueError("Marble is already in goal area")
        
        new_position = marble_position
        for i in range(4):
            new_position = [s for s in self.board_graph.predecessors(new_position)][0]
            # it could be that marble is aiming to pass a protected marble
            # on the start field
            if self.graph_data["protected"][new_position]:
                raise ValueError("way is blocked by a marble on the start field!")
            
        # final check for position to be free and kick other marble if possible
        kicked_color = self.graph_data["occupied"][new_position]
        if kicked_color != 'False':
            kicked_label = self.graph_data["label"][new_position]
            # set the marble to a free field in the start area
            self.kick(kicked_color, kicked_label)
                            
        # delete marble from old position
        self.graph_data["occupied"][marble_position] = "False"
        self.graph_data["label"][marble_position] = math.nan
        self.graph_data["protected"][marble_position] = False
        # put marble on the new spot
        self.graph_data["occupied"][new_position] = color
        self.graph_data["label"][new_position] = label
        
        # turn on warnings again
        warnings.filterwarnings("default")
        
        # plot new board
        if plot:
            self.plot()
    
    def exchange(self, color1, label1, color2, label2, plot = True):
        # temporarily turn off warnings
        warnings.filterwarnings("ignore")
        # first marble
        occupied1_bool = np.array(self.graph_data["occupied"] == color1)
        label1_bool = np.array(self.graph_data["label"] == label1)
        marble1_position = int(np.argwhere(occupied1_bool * label1_bool))
        # second marble
        occupied2_bool = np.array(self.graph_data["occupied"] == color2)
        label2_bool = np.array(self.graph_data["label"] == label2)
        marble2_position = int(np.argwhere(occupied2_bool * label2_bool))
        
        # check if marbles are exchangeable
        self.exchangeable(marble1_position)
        self.exchangeable(marble2_position)
        # exchange marbles
        self.graph_data["occupied"][marble2_position] = color1
        self.graph_data["label"][marble2_position] = label1
        self.graph_data["occupied"][marble1_position] = color2
        self.graph_data["label"][marble1_position] = label2
        
        # plot new board
        if plot:
            self.plot()
    
    def execute_action(self, action, color1, label1 = None, color2 = None, label2 = None, direction = None, plot = True):
        # input standardization
        try:
            action = int(action)
        except:
            pass
        # remember old state
        old_state = self.graph_data.copy(deep = True)
        action_executed = False
        while not action_executed:
            action_executed = True
            if action == 'out':
                self.out(color1, plot = False)
            elif action == 'exchange':
                self.exchange(color1, label1, color2, label2, plot = False)
            elif action == 7:
                # if there is only one moveable marble take this one
                if label1 in ["A", "B", "C", "D"]:
                    self.single_steps(color1, label1, 7, plot = True)
                else:
                    # otherwise distribute steps among marbles
                    remaining_steps = 7
                    while remaining_steps > 0:
                        # choose marble
                        label = 0
                        while not label in ["A", "B", "C", "D"]:
                            dialog_message = "Player " + color1 + ": which marble shall be moved? ("  + str(remaining_steps) + " steps remaining)"
                            label = tk.simpledialog.askstring(title="Action", prompt=dialog_message)
                        # compute maximum number of steps for chosen marble
                        no_steps_possible = self.check_steps_possible(color1, label, remaining_steps)
                        # if no more steps possible, ask user again which marble to move
                        steps = None
                        if no_steps_possible == 0:
                            continue
                        # if only one step possible, automatically choose 1
                        elif no_steps_possible == 1:
                            steps = 1
                        else:
                            # choose number of steps yourself
                            while not steps in range(1, no_steps_possible + 1):
                                dialog_message = color1 + " marble " + label + ": how many steps? (" + str(remaining_steps) + " steps remaining, maximal " + str(no_steps_possible) + " steps possible for this marble)"
                                steps = tk.simpledialog.askstring(title="Action", prompt=dialog_message)
                                try:
                                    steps = int(steps)
                                except:
                                    pass
                        remaining_steps = remaining_steps - steps
                        # apply number of steps
                        self.single_steps(color1, label, steps, plot = True)
                        # check if goal has been reached with last marble (special rule for 7) and change color if so
                        # watch out for special case when team wins by getting marbles of both colors into the goal area
                        finished_own_color = False
                        if self.check_finished(color1):
                            if finished_own_color:
                                return(True)
                            else:
                                finished_own_color = True
                                color1 = utils.partner(color1)
               
            elif action == 4:
                if direction == "f":
                    self.move_forwards(color1, label1, 4, plot = False)
                elif direction == "b":
                    self.move_backwards(color1, label1, plot = False)
                
            elif isinstance(action, int):
                self.move_forwards(color1, label1, action, plot = False)
        # if everything worked as intented remember old_state
        self.state_history.append(old_state)
        if plot:
            self.plot()
        # if game has not been won with 7
        return(False)
    
    def reverse_action(self):
        actions_played = len(self.state_history)
        if actions_played == 0:
            raise ValueError("No actions have been played yet")
        self.graph_data = self.state_history[-1]
        self.state_history = self.state_history[0:(actions_played-1)]
        self.plot()
        
    def plot(self): 
        # line thickness
        casual_fields = self.graph_data['color'].isna()
        thickness = [5.0 - casual_fields[i] * 4.0 for i in range(self.n_nodes)]
        #  field colors
        colors = self.graph_data['color'].fillna("grey")
        # placing marbles
        occupation = self.graph_data['occupied'].replace("False", "#EED5AE")
        # labeling marbles
        currently_occupied = self.graph_data[self.graph_data['occupied'] != "False"]
        label_dictionary = currently_occupied[["label"]].to_dict()['label']
        label_pos_dictionary = dict([[key, self.position_data.get(key)] for key in currently_occupied["id"]])
        
        fig, ax = plt.subplots(figsize=(16, 16), dpi=160, facecolor = "#EED5AE")
        ax.set_facecolor("#EED5AE")
        nx.draw_networkx_nodes(self.board_graph, pos = self.position_data, node_color = occupation, 
                               edgecolors = colors, linewidths = thickness, node_size = 2000)   
        nx.draw_networkx_labels(self.board_graph, pos = label_pos_dictionary, 
                                labels = label_dictionary, font_size = 36) 
        plt.show()
            
