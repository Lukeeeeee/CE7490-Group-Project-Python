from src.core import Basic
import networkx as nx


class Server(Basic):

    def __init__(self, serer_id):
        super().__init__()
        self.graph = nx.Graph()
        self.id = serer_id

    def add_node(self, node_id, node_type, write_freq):
        self.graph.add_node(node_id,
                            node_type=node_type,
                            write_freq=write_freq)

    def get_node(self, node_id):
        if self.graph.has_node(node_id):
            return self.graph.nodes[node_id]
        else:
            print("Node %d not existed" % (node_id))
            return False

    def get_load(self):
        return self.graph.order()

    def has_node(self, node_id):
        return self.graph.has_node(node_id)

    def remove_node(self, node_id):
        self.graph.remove_node(node_id)
