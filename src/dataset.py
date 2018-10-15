from src.core import Basic
import networkx as nx
import numpy as np

class Dataset(Basic):
    def __init__(self, dataset_str):
        super().__init__()
        self.graph = self.load_dataset(dataset_str)

    def load_dataset(self,dataset_str):
        g = nx.Graph()
        # Load dataset
        if dataset_str == 'facebook':
            edgelist = np.loadtxt(r'C:\Users\user\Desktop\CE7490-Group-Project-Python-L1\dataset\Facebook.txt',int)
        elif dataset_str == 'twitter':
            edgelist = np.loadtxt(r'C:\Users\user\Desktop\CE7490-Group-Project-Python-L1\dataset\Twitter.txt',int)
        elif dataset_str == 'twitters1':
            edgelist = np.loadtxt(r'C:\Users\user\Desktop\CE7490-Group-Project-Python-L1\dataset\TwittersSample1.txt',int)
        elif dataset_str == 'twitters2':
            edgelist = np.loadtxt(r'C:\Users\user\Desktop\CE7490-Group-Project-Python-L1\dataset\TwittersSample2.txt',int)
        elif dataset_str == 'amazon':
            edgelist = np.loadtxt(r'C:\Users\user\Desktop\CE7490-Group-Project-Python-L1\dataset\Amazon.txt',int)
        elif dataset_str == 'amazons':
            edgelist = np.loadtxt(r'C:\Users\user\Desktop\CE7490-Group-Project-Python-L1\dataset\AmazonSample.txt',int)
        elif dataset_str == 'p2pgnutella':
            edgelist = np.loadtxt(r'C:\Users\user\Desktop\CE7490-Group-Project-Python-L1\dataset\p2pGnutella.txt',int)
        else:
            pass
        g.add_edges_from(edgelist)
        return g

    def get_all_adj_node_id_list(self, node_id):
        return list(self.graph[node_id])

    def has_edge(self, s_node_id, t_node_id):
        if t_node_id in self.graph.adj[s_node_id]:
            return True
        else:
            return False

