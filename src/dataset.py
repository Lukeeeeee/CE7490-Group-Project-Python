from src.core import Basic
import networkx as nx
import numpy as np
from dataset import DATASET_PATH
import os


class Dataset(Basic):
    def __init__(self, dataset_str, part_flag=None):
        super().__init__()
        self.graph = self.load_dataset(dataset_str)
        self.node_list = list(self.graph.nodes)
        if part_flag:
            split_index = int(len(self.node_list) * part_flag)

            for i in range(split_index, len(self.node_list)):
                self.graph.remove_node(n=self.node_list[i])

    def load_dataset(self, dataset_str):
        g = nx.Graph()
        edgelist = []
        if dataset_str == 'facebook':
            edgelist = np.loadtxt(os.path.join(DATASET_PATH, 'Facebook.txt'), int)
        elif dataset_str == 'twitter':
            edgelist = np.loadtxt(os.path.join(DATASET_PATH, 'Twitter.txt'), int)
        elif dataset_str == 'twitters1':
            edgelist = np.loadtxt(os.path.join(DATASET_PATH, 'TwitterSample1.txt'), int)
        elif dataset_str == 'twitters2':
            edgelist = np.loadtxt(os.path.join(DATASET_PATH, 'TwitterSample2.txt'), int)
        elif dataset_str == 'amazon':
            edgelist = np.loadtxt(os.path.join(DATASET_PATH, 'AmazonSample.txt'), int)
        elif dataset_str == 'amazons':
            edgelist = np.loadtxt(os.path.join(DATASET_PATH, 'AmazonSample.txt'), int)
        elif dataset_str == 'p2pgnutella':
            edgelist = np.loadtxt(os.path.join(DATASET_PATH, 'p2pGnutella.txt'), int)
        else:
            pass
        g.add_edges_from(edgelist)
        return g

    def get_all_adj_node_id_list(self, node_id):
        return list(self.graph[node_id])

    def has_edge(self, s_node_id, t_node_id):
        if t_node_id in list(self.graph.adj[s_node_id]):
            return True
        else:
            return False
