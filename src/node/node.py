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
        assert Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER <= len(server_list) - 1
        tmp_server_list = [(i, server_list[i], server_list[i].get_load()) for i in range(len(server_list))]
        tmp_server_list.sort(key=lambda x: x[2])
        for res in tmp_server_list:
            if len(self.virtual_primary_copy_server_list) >= Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER:
                return
            if server_list[res[0]].id != self.server_id and (server_list[res[0]].has_node(node_id=self.id,
                                                                                          node_type=Constant.VIRTUAL_PRIMARY_COPY) is False):
                self.add_virtual_primary_copy(target_server=server_list[res[0]])

    def add_non_primary_copy(self, target_server):
        if target_server in self.non_primary_copy_server_list and \
                target_server.has_node(self.id, node_type=Constant.NON_PRIMARY_COPY):
            # TODO check for this
            return
        if int(target_server in self.non_primary_copy_server_list) + \
                int(target_server.has_node(self.id, node_type=Constant.NON_PRIMARY_COPY)) == 1:
            raise ValueError
        target_server.add_node(node_id=self.id, node_type=Constant.NON_PRIMARY_COPY, write_freq=Constant.WRITE_FREQ)
        self.non_primary_copy_server_list.append(target_server)

    def add_virtual_primary_copy(self, target_server):
        # TODO check for this

        if target_server in self.virtual_primary_copy_server_list and target_server.has_node(self.id,
                                                                                             node_type=Constant.VIRTUAL_PRIMARY_COPY):
            return

        if int(target_server in self.virtual_primary_copy_server_list) + \
                int(target_server.has_node(self.id, node_type=Constant.VIRTUAL_PRIMARY_COPY)) == 1:
            raise ValueError

        self.virtual_primary_copy_server_list.append(target_server)
        target_server.add_node(node_id=self.id, node_type=Constant.VIRTUAL_PRIMARY_COPY,
                               write_freq=Constant.WRITE_FREQ)
