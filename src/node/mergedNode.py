from src.node.node import Node
import networkx as nx
from src.core import Basic
from copy import deepcopy as dp
import numpy as np
from src.constant import Constant


class MergedNode(Basic):
    def __init__(self, node, ID, server, algo):
        super().__init__()
        self.node_list = [node]
        node.merged_node_id = ID
        self.node_id_list = [ID]
        self.internal_connection = 0
        self.external_connection = len(list(algo.network_dataset.graph[ID]))
        self.id = ID
        self.server = server
        print("new merged node %d with node %d, server %d" % (self.id, self.node_id_list[0], server.id))

    @property
    def merge_process_metric_beta(self):
        return (self.internal_connection - self.external_connection) / self.node_count

    @property
    def node_count(self):
        assert len(self.node_id_list) == len(self.node_list)
        return len(self.node_list)

    def _add_node(self, node, algo, remove_flag=True):
        prev_node_id = node.id
        assert isinstance(node, MergedNode)
        for node_i in node.node_list:
            self._add_single_node(node=node_i, algo=algo, remove_flag=remove_flag)

        if remove_flag is True:
            original_merged_node = list(filter(lambda x: x.id == prev_node_id, algo.merged_node_list))
            if len(original_merged_node) != 1:
                print("%d" % node.id, self.node_id_list)
                pass
            assert len(original_merged_node) == 1
            original_merged_node = original_merged_node[0]
            algo.merged_node_list.remove(original_merged_node)

    def _add_single_node(self, node, algo, remove_flag=True):
        inside_degree = 0
        for node_s in self.node_id_list:
            # Add internal connection count if has edge, also remove external connection
            if node.id in list(algo.network_dataset.graph[node_s]):
                self.internal_connection += 1
                self.external_connection -= 1
                inside_degree += 1
        # Add external connection with node that connected with new add node and not in the merged node
        self.external_connection += len(algo.network_dataset.graph[node.id]) - inside_degree

        self.node_list.append(node)
        self.node_id_list.append(node.id)

        node.merged_node_id = self.id
        print("node %d was merged into %d, node_list=" % (node.id, self.id), self.node_id_list)

    def launch_merge_node_process(self, algo):
        rand_index = np.arange((len(self.node_list)))
        np.random.shuffle(rand_index)
        for node_index in rand_index:
            while True:
                merged_flag = False
                node = self.node_list[node_index]
                adj_node_list = list(algo.network_dataset.graph[node.id])
                adj_node_index = np.arange(len(adj_node_list))
                np.random.shuffle(adj_node_index)
                for index_i in adj_node_index:
                    adj_node_id = adj_node_list[index_i]
                    if adj_node_id not in self.node_id_list:
                        to_merge_node = algo.get_merged_node_with_id(adj_node_id)
                        copyed_adj_node = dp(to_merge_node)
                        copyed_temp_node = dp(self)
                        copyed_temp_node._add_node(node=copyed_adj_node, algo=dp(algo), remove_flag=False)
                        if copyed_temp_node.merge_process_metric_beta > self.merge_process_metric_beta:
                            self._add_node(node=to_merge_node, algo=algo)
                            merged_flag = True
                if not merged_flag:
                    break

    def remove_one_node(self, node, algo):
        self.node_list.remove(node)
        self.node_id_list.remove(node.id)
        inside_degree = 0
        for node_s in self.node_id_list:
            # Add internal connection count if has edge, also remove external connection
            if node.id in list(algo.network_dataset.graph[node_s]):
                self.internal_connection -= 1
                self.external_connection += 1
                inside_degree += 1
        # Add external connection with node that connected with new add node and not in the merged node
        self.external_connection -= len(algo.network_dataset.graph[node.id]) - inside_degree
        pass
