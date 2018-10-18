from src.node.node import Node
import networkx as nx
from src.core import Basic
from copy import deepcopy as dp


class MergedNode(Basic):
    def __init__(self, ID):
        super().__init__()
        self.node_list = []
        self.node_id_list = []
        self.internal_connection = 0
        self.external_connection = 0
        self.id = ID
        self.external_node_id_list = []

    @property
    def merge_process_metric_beta(self):
        return (self.internal_connection - self.external_connection) / self.node_count

    @property
    def node_count(self):
        return len(self.node_list)

    def add_node(self, node, algo):
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

    def launch_merge_node_process(self, algo):
        for node in self.node_list:
            for adj_node_id in list(algo.dataset_graph.graph[node.id]):
                if adj_node_id not in self.node_id_list:
                    res = self.merge_node(target_node=algo.get_node_wtih_id(adj_node_id),
                                          algo=algo)

    def merge_node(self, target_node, algo):
        temp_node = dp(self)
        temp_node.add_node(node=target_node, algo=algo)
        if temp_node.merge_process_metric_beta > self.merge_process_metric_beta:
            pass

        return False
