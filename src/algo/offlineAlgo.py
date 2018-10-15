from src.core import Basic
from src.constant import Constant


class OfflineAlgo(Basic):
    def __init__(self, server_list, dataset):
        super().__init__()
        self.ETA = Constant.OFFLINE_ETA
        self.EPSILON = Constant.OFFLINE_EPSILON
        self.server_list = server_list
        self.dataset = dataset

    def add_new_node(self, node_id, node_type, write_freq):
        min_server = self.server_list[0]
        for server in self.server_list:
            if server.get_load() < min_server.get_load():
                min_server = server
        min_server.add_node(node_id=node_id,
                            node_type=node_type,
                            write_freq=write_freq)

    def add_node_to_server(self, node_id, node_type, write_freq, server):
        server.add_node(node_id=node_id, node_type=node_type, write_freq=write_freq)
        adj_node_list = self.dataset.get_all_adj_node_id_list(node_id=node_id)
        for adj_node in adj_node_list:
            pass

    def get_primary_copy_server(self, node_id):
        for server in self.server_list:
            if server.

    def check_node_locality(self, node, adj_node):
        pass
