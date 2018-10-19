from src.node.node import Node
import networkx as nx
from src.core import Basic
from copy import deepcopy as dp
import numpy as np
from src.constant import Constant


class MergedNode(Basic):
    def __init__(self, ID, server):
        super().__init__()
        self.node_list = []
        self.node_id_list = []
        self.internal_connection = 0
        self.external_connection = 0
        self.id = ID
        self.server = server
        self.external_node_id_list = []

    @property
    def merge_process_metric_beta(self):
        return (self.internal_connection - self.external_connection) / self.node_count

    @property
    def node_count(self):
        return len(self.node_list)

    def _add_node(self, node, algo):
        inside_degree = 0
        for node_s in self.node_list:
            # Add internal connection count if has edge, also remove external connection
            if node.id in list(algo.dataset_graph.graph[node_s]):
                self.internal_connection += 1
                self.external_connection -= 1
                inside_degree += 1
        # Add external connection with node that connected with new add node and not in the merged node
        self.external_connection += len(algo.dataset_graph[node.id]) - inside_degree

        self.node_list.append(node)
        self.node_id_list.append(node.id)
        node.merged_node_id = self.id
        algo.merged_node_list.remove(node)

    def launch_merge_node_process(self, algo):
        rand_index = np.arange((len(self.node_list)))
        np.random.shuffle(rand_index)
        for node_index in rand_index:
            while True:
                merged_flag = False
                node = self.node_list[node_index]
                adj_node_list = list(algo.dataset_graph.graph[node.id])
                adj_node_index = np.arange(len(adj_node_list))
                np.random.shuffle(adj_node_index)
                # TODO control the random process
                for index_i in adj_node_index:
                    adj_node_id = adj_node_list[index_i]
                    if adj_node_id not in self.node_id_list:
                        temp_node = dp(self)
                        adj_node = algo.get_node_with_id(adj_node_id)
                        temp_node._add_node(node=adj_node, algo=algo)
                        if temp_node.merge_process_metric_beta > self.merge_process_metric_beta:
                            self._add_node(node=adj_node, algo=algo)
                            merged_flag = True
                if not merged_flag:
                    break
