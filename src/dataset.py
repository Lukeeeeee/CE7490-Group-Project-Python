from src.core import Basic
import networkx as nx


class Dataset(Basic):
    def __init__(self, dataset_str):
        super().__init__()
        if dataset_str == 'facebook':
            self.graph = self.load_facebook_dataset()
        else:
            pass

    def load_facebook_dataset(self):
        g = nx.Graph()

        # Load dataset

        return g

    def get_all_adj_node_id_list(self, node_id):
        return list(self.graph[node_id])
