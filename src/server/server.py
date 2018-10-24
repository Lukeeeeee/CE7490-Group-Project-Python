from src.core import Basic
import networkx as nx
from src.constant import Constant
import logging


class Server(Basic):

    def __init__(self, serer_id):
        super().__init__()
        self.graph = nx.Graph()
        self.id = serer_id
        self.primary_copy_node_list = []

    def add_node(self, node_id, node_type, write_freq):
        if self.has_node(node_id=node_id, node_type=node_type):
            raise ValueError('Node %d existed' % node_id)
        self.graph.add_node(node_id,
                            node_type=node_type,
                            write_freq=write_freq)
        if node_type == Constant.PRIMARY_COPY:
            self.primary_copy_node_list.append(node_id)

    def get_node(self, node_id):
        if self.graph.has_node(node_id):
            return self.graph.nodes[node_id]
        else:
            log_str = "Node %d not existed" % node_id
            logging.info(log_str)
            print(log_str)
            return False

    def get_load(self):
        return self.graph.order()

    def has_node(self, node_id, node_type=None):
        if node_type:
            return self.graph.has_node(node_id) and self.graph.nodes[node_id]['node_type'] == node_type
        else:
            return self.graph.has_node(node_id)

    def remove_node(self, node_id, node_type=None):
        if node_type:
            if self.graph.nodes[node_id]['node_type'] == node_type:
                self._remove_node(node_id=node_id)
        else:
            self._remove_node(node_id=node_id)

    def _remove_node(self, node_id):
        if self.graph.nodes[node_id]['node_type'] == Constant.PRIMARY_COPY:
            self.primary_copy_node_list.remove(node_id)
        self.graph.remove_node(node_id)

    def return_type_nodes(self, node_type):
        res = filter(lambda x: self.graph.nodes[x]['node_type'] == node_type, list(self.graph.nodes))
        return list(res)
