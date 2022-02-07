'''
Created on 26/03/2018

@author: gtexier
'''
import os
# import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from graph_creation.intersection import Intersection as inter
import graph_creation.orientation as orient
from graph_creation.orientation import Orientation as ori


class Labyrinth():
    entry_name = "ENTRY"
    exit_name = "EXIT"

    def __init__(self, name):
        self.name = name        #first_node = LabyrinthNode('Entry', nc=None, ec=None, wc=None, sc=None)
        self.tree = nx.DiGraph()

    def draw(self):
        pos = nx.spring_layout(self.tree)
        nbnodes = self.tree.number_of_nodes()
        labels = dict()
        nodes = self.tree.nodes()
        print(nodes)
        for i in range(nbnodes-1):
            labels[i] = str(i)
        nx.draw_networkx_nodes(self.tree, pos, node_color='b')
        nx.draw_networkx_edges(self.tree, pos, with_labels = True)
        nx.draw_networkx_edge_labels(self.tree,pos)
        nx.draw_networkx_labels(self.tree, pos)#, labels)
        #nbnodes = self.tree.number_of_nodes()
        plt.show()

    def print_text_graph(self):
        edge_set = nx.edges(self.tree)
        # for e in edge_set:
        #     print("GRAPH", "edge from ", e[0], " to ", e[1], " dir = ", orient.get_orientation_label(self.tree.get_edge_data(e[0], e[1])['label']))
        list_edge = []
        for e in edge_set:
            list_edge.append(e)
        list_edge.sort()
        for e in list_edge:
            print("GRAPH", "edge from ", e[0], " to ", e[1], " dir = ", orient.get_orientation_label(self.tree.get_edge_data(e[0], e[1])['label']))
        return list_edge.sort()


    def add_intersection(self, type_intersection, parent_name, dir):
        # parent = self.stack.pop()
        # self.current_name = self.current_name + 1
        print("GRAPH - add intersection type ",str(type_intersection))
        if type_intersection == inter.DEAD_END:
            pass
#             id_node = self.get_new_node_name()
#             self.tree.add_node(id_node)
#             child_dir = dir
#             inv_child_dir = orient.inverse_direction(child_dir)
#             self.tree.add_edge(parent_name, id_node, label=child_dir)
#             self.tree.add_edge(id_node,
#                                parent_name,
#                                label=inv_child_dir)
        elif type_intersection == inter.FRONT_LEFT:
            # Front child creation
            child_dir = dir
            self.add_new_node(parent_name, child_dir)
            # Left child creation
            child_dir = orient.get_left(dir)
            self.add_new_node(parent_name, child_dir)
        elif type_intersection == inter.FRONT_RIGHT:
            # Front child creation
            child_dir = dir
            self.add_new_node(parent_name, child_dir)
            # Right child creation
            child_dir = orient.get_right(dir)
            self.add_new_node(parent_name, child_dir)
        elif type_intersection == inter.LEFT_RIGHT:
            # Left child creation
            child_dir = orient.get_left(dir)
            self.add_new_node(parent_name, child_dir)
            # Right child creation
            child_dir = orient.get_right(dir)
            self.add_new_node(parent_name, child_dir)
        elif type_intersection == inter.FRONT_LEFT_RIGHT:
            # Front child creation
            child_dir = dir
            self.add_new_node(parent_name, child_dir)
            # Left child creation
            child_dir = orient.get_left(dir)
            self.add_new_node(parent_name, child_dir)
            # Right child creation
            child_dir = orient.get_right(dir)
            self.add_new_node(parent_name, child_dir)
        elif type_intersection == inter.TURN_LEFT:
            # Left child creation
            child_dir = orient.get_left(dir)
            self.add_new_node(parent_name, child_dir)
        elif type_intersection == inter.TURN_RIGHT:
            # Right child creation
            child_dir = orient.get_right(dir)
            self.add_new_node(parent_name, child_dir)

    def add_new_node(self, parent_name, dir):
        id_node = self.get_new_node_name()
        self.tree.add_node(id_node)
        child_dir = dir
        inv_child_dir = orient.inverse_direction(child_dir)
        self.tree.add_edge(parent_name, id_node, label=child_dir)
        self.tree.add_edge(id_node,
                           parent_name,
                           label=inv_child_dir)
        print("GRAPH - add new node ", id_node, " parent : ", parent_name, " direction : ", child_dir)

    def get_new_node_name(self):
        nb = len(self.tree)
        id_node = "TBE"+str(nb)
        return id_node

    def add_entry(self, dir):
            # EXIT Node creation
            self.tree.add_node(self.entry_name)
            new_name = self.get_new_node_name()
            print(new_name)
            self.add_new_node(self.entry_name, dir)
#             self.tree.add_node(new_name)
#             child_dir = orient.get_right(dir)
#             inv_child_dir = orient.inverse_direction(child_dir)
#             self.tree.add_edge(self.entry_name, new_name, label=child_dir)
#             self.tree.add_edge(new_name,
#                                self.entry_name,
#                                label=inv_child_dir)

    def add_exit(self, tmp_name, dir):
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
        else:
            print("erreur le noeud n'existe pas ", tmp_name)
        print("GRAPH", "add exit", "parent : ", tmp_name)

    def getRacine(self):
        liste_nodes = self.tree.node()
        return liste_nodes[self.entry_name]

    def get_dir_child(self, node_name, dir):
        print('get_dir_child ' + node_name)
        liste_nodes = self.tree.node()
        # node_src = liste_nodes[node_name]
        print(self.tree.successors(self.entry_name))
        succ = self.tree.successors(node_name)
        for s in succ:
            if self.tree.get_edge_data(node_name, s)['label'] == dir:
                return self.name

    def go_to_next(self, parent, dir):
        # print("parent and dir ", parent, dir)
        if parent == self.exit_name:
            return self.exit_name
        else:
            succ = self.tree.successors(parent)
            # print("succ of parent", succ, parent, dir)
            for s in succ:
                edge_data = self.tree.get_edge_data(parent, s)
                # print("edge of succ ", edge_data, dir)
                if edge_data['label'] == dir:
                    return s
            return NameError


def main():
    lab = Labyrinth('mylab')
    lab.add_entry(ori.NORTH)
    s = lab.go_to_next(lab.entry_name, ori.NORTH)
    lab.add_intersection(inter.LEFT_RIGHT, s, ori.NORTH)
    fork1 = s
    s = lab.go_to_next(s, ori.WEST)
    lab.add_intersection(inter.TURN_RIGHT, s, ori.WEST)
    s = lab.go_to_next(s, ori.NORTH)
    lab.add_intersection(inter.DEAD_END, s, ori.WEST)
    s = lab.go_to_next(fork1, ori.EAST)
    lab.add_intersection(inter.TURN_LEFT, s, ori.EAST)
    s = lab.go_to_next(s, ori.NORTH)
    lab.add_intersection(inter.FRONT_LEFT_RIGHT, s, ori.NORTH)
    fork2 = s
    s = lab.go_to_next(fork2, ori.WEST)
    lab.add_intersection(inter.DEAD_END, s, ori.WEST)
    s = lab.go_to_next(fork2, ori.EAST)
    lab.add_intersection(inter.DEAD_END, s, ori.EAST)
    s = lab.go_to_next(fork2, ori.NORTH)
    lab.add_exit(s, ori.NORTH)
    lab.draw()


if __name__ == "__main__":
    main()
