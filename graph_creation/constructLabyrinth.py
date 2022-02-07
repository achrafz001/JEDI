'''
Created on 26/03/2018

@author: gtexier
SAR WARS Creation de graphes
'''
import os
# import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from intersection import Intersection as inter
import orientation as orient
from orientation import Orientation as ori


class Labyrinth():
    entry_name = "ENTRY"
    exit_name = "EXIT"

    def __init__(self, name):
        self.name = name
        # self.tree = nx.DiGraph()
        self.tree = nx.DiGraph()

    def add_intersection(self, type_intersection, parent_name, dir):
        '''
        Adds an intersection to the graph
        Parameters:
            type_intersection: what kind of intersection to add
            parent_name: name of the nodes where to insert the intersection
            dir: the direction of the robot
        '''
        # Ajoutez le code pour gérer l'insertion des différents types d'intersection
        # if type_intersection == ..... :
        #    .....
        # elif type_intersection == .....:
        #    .....
        # etc...
        if type_intersection == inter.PathTwoRight:
            child_dir=orient.get_right(dir)
            self.add_new_node(parent_name, child_dir)
        elif type_intersection == inter.PathTwoLeft:
            child_dir= orient.get_left(dir)
            self.add_new_node(parent_name, child_dir)
        elif type_intersection == inter.PathThreeLeftFront:
            child_dir=dir
            self.add_new_node(parent_name, child_dir)
            child_dir=orient.get_left(dir)
            self.add_new_node(parent_name, child_dir)  
        elif type_intersection == inter.PathThreeRightFront:
            child_dir=dir
            self.add_new_node(parent_name, child_dir)
            child_dir=orient.get_right(dir)
            self.add_new_node(parent_name, child_dir) 
        elif type_intersection == inter.PathThreeLeftRight:
            child_dir=orient.get_right(dir)
            self.add_new_node(parent_name, child_dir)
            child_dir=orient.get_left(dir)
            self.add_new_node(parent_name, child_dir)


    def add_new_node(self, parent_name, dir):
        '''
        Adds a new node to the graph
        Parameters:
            parent_name: name of the nodes where to insert the intersection
            dir: the direction of the robot
        '''
        # Ajoutez le code pour ajouter un nouveau sommet dans le graphe
        # dans lequel vous gérez le nom du nouveau sommet
        self.tree.add_node("HAN"+str(len(self.tree)))
        child_dir = dir
        self.tree.add.edge(parent_name, "HAN"+str(len(self.tree)), child_dir)
        inv_dir= orient.inverse_direction(dir)
        self.tree.add.edge("HAN"+str(len(self.tree)), parent_name, inv_dir)

    def add_entry(self, dir):
        '''
        Adds the first node of the graph, corresponding to the entry of
        the labyrinth. This node is named ENTRY
        Parameters:
            dir: the direction of the robot
        '''
        # Ajoutez le code pour ajouter le sommet ENTRY dans le graphe
        self.tree.add_node(self.entry_name)
        self.add_new_node(self.entry_name, dir) 

    def add_exit(self, tmp_name, dir):
        '''
        Adds the node named EXIT to the graph, corresponding to the exit of
        the labyrinth.
        Parameters:
            dir: the direction of the robot
        '''
        # Ajoutez le code pour ajouter le sommet EXIT dans le graphe
        if tmp_name == self.entry_name:
            self.add_new_node(self, tmp_name, dir)
        elif self.tree.has_node(tmp_name):
            self.tree.add_node(self.exit_name)
            for p in self.tree.predecessors(tmp_name):
                data_edge = self.tree.get_edge_data(p, tmp_name)
                self.tree.add_edge(p, self.exit_name, label=data_edge['label'])
            for s in self.tree.successors(tmp_name):
                data_edge = self.tree.get_edge_data(tmp_name, s)
                self.tree.add_edge(self.exit_name, s, label=data_edge['label'])
            self.tree.remove_node(tmp_name)
            #
        else:
            print("erreur le noeud n'existe pas ", tmp_name)
        print("GRAPH", "add exit", "parent : ", tmp_name)
        


    def get_dir_child(self, parent_name, dir):
        '''
        Returns the name of  a new node to the graph
        Parameters:
            parent_name: name of the parent nodes
            dir: the direction of child node whose name is asked
        '''
        # Ajoutez le code pour retourner le nom du sommet fils de parent_name
        # dans la direction dir
        print('get_dir_child ' + parent_name)
        liste_nodes = self.tree.node()
        # node_src = liste_nodes[node_name]
        print(self.tree.successors(self.entry_name))
        succ = self.tree.successors(parent_name)
        for s in succ:
            if self.tree.get_edge_data(parent_name, s)['label'] == dir:
                return self.name
        

    def go_to_next(self, parent_name, dir):
        '''
        Returns the name of the child node we will reach from parent_name
        when going in the direction dir
        Parameters:
            parent_name: name of the parent nodes
            dir: the direction of child node where we want to go
        '''
        # Ajoutez le code pour retourner le nom du sommet fils de parent_name
        # dans la direction dir. Gerez le cas ou ce sommet n'existe pas.
        pass

    def draw(self, withlabels=True):
        '''
        Draws the graph
        Parameters:
            withlabels: if True the label of the edges is shown, else it
            is hidden
        '''
        # Ajoutez le code pour afficher le graphe.
        # Choisissez votre representation.
        pass


def main():
    # Ajoutez votre code pour instancier un graphe et creer un graphe
    # correspondant a un labyrinthe
    pass


if __name__ == "__main__":
    main()
