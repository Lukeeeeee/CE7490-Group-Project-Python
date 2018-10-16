from src.core import Basic
from src.constant import Constant
from src.node.node import Node


class Algo(Basic):
    def __init__(self, server_list, network_dataset):
        super().__init__()
        self.server_list = server_list
        self.network_dataset = network_dataset
        self.node_list = []

    def add_new_primary_node(self, node_id, write_freq):
        raise NotImplementedError
