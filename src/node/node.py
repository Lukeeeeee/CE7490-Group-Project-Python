from src.core import Basic
import networkx as nx
from src.constant import Constant
import numpy as np


class Node(Basic):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.server = None
        self.non_primary_copy_server_list = []
        self.virtual_primary_copy_server_list = []

    def assign_virtual_primary_copy(self, server_list):
        least_virtual_primary_count = min(Constant.LEASET_VIRTUAL_PRIMARY_COPY_NUMBER, len(server_list) - 1)
        for _ in range(least_virtual_primary_count):
            server_id = self.server.id
            while server_list[server_id].id == self.server.id:
                server_id = np.random.randint(low=0, high=len(server_list))
            self.virtual_primary_copy_server_list.append(server_id)
            server_list[server_id].add_node(node_id=self.id, node_type=Constant.VIRTUAL_PRIMARY_COPY, write_freq=0.0)
