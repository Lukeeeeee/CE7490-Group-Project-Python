from src.core import Basic
from src.constant import Constant
from src.node.node import Node


class OfflineAlgo(Basic):
    def __init__(self, server_list, dataset):
        super().__init__()
        self.ETA = Constant.OFFLINE_ETA
        self.EPSILON = Constant.OFFLINE_EPSILON
        self.server_list = server_list
        self.dataset = dataset
        self.node_list = []

    def add_new_primary_node(self, node_id, node_type, write_freq):
        min_server = self.server_list[0]
        new_node = Node(id=node_id)
        self.node_list.append(new_node)
        for server in self.server_list:
            if server.get_load() < min_server.get_load():
                min_server = server
        new_node.server = min_server
        min_server.add_node(node_id=node_id,
                            node_type=node_type,
                            write_freq=write_freq)

    def add_node_to_server(self, node_id, node_type, write_freq, server):
        server.add_node(node_id=node_id, node_type=node_type, write_freq=write_freq)
        adj_node_list = self.dataset.get_all_adj_node_id_list(node_id=node_id)
        for adj_node in adj_node_list:
            if not self.check_node_locality(node_id=node_id, adj_node_id=adj_node):
                pr_adj_node_server = self.get_primary_copy_server(node_id=adj_node)

    def get_primary_copy_server(self, node_id):
        res = None
        for server in self.server_list:
            pr_node = server.get_node(node_id=node_id)
            if not pr_node and pr_node['NODE_TYPE'] == Constant.PRIMARY_COPY:
                if res is not None:
                    raise RuntimeError("Multiple primary copy existed")
                res = server
                break
        return res

    def check_node_locality(self, node_id, adj_node_id):
        node = self.get_node_with_id(node_id=node_id)
        adj_node = self.get_node_with_id(node_id=adj_node_id)
        if node is None or adj_node is Node:
            return True

    def get_node_with_id(self, node_id):
        for node in self.node_list:
            if node.id == node_id:
                return node
        return None
