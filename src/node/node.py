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
        self.merged_node_id = -1

    @property
    def server_id(self):
        if self.server:
            return self.server.id
        else:
            return None

    def assign_virtual_primary_copy(self, server_list):
        least_virtual_primary_count = min(Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER, len(server_list) - 1)
        for _ in range(least_virtual_primary_count):
            server_id = self.server.id
            while server_list[server_id].id == self.server.id or server_list[server_id].has_node(node_id=self.id,
                                                                                                 node_type=Constant.VIRTUAL_PRIMARY_COPY):
                server_id = np.random.randint(low=0, high=len(server_list))
            self.add_virtual_primary_copy(target_server=server_list[server_id])

    def add_non_primary_copy(self, target_server):
        target_server.add_node(node_id=self.id, node_type=Constant.NON_PRIMARY_COPY, write_freq=Constant.WRITE_FREQ)
        self.non_primary_copy_server_list.append(target_server)

    def add_virtual_primary_copy(self, target_server):
        self.virtual_primary_copy_server_list.append(target_server)
        target_server.add_node(node_id=self.id, node_type=Constant.VIRTUAL_PRIMARY_COPY,
                               write_freq=Constant.WRITE_FREQ)
