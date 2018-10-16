from src.core import Basic
from src.constant import Constant
from src.node.node import Node
from src.algo.inter_server_cost import compute_inter_sever_cost


class OfflineAlgo(Basic):
    def __init__(self, server_list, network_dataset):
        super().__init__()
        self.ETA = Constant.OFFLINE_ETA
        self.EPSILON = Constant.OFFLINE_EPSILON
        self.server_list = server_list
        self.network_dataset = network_dataset
        self.node_list = []

    def add_new_primary_node(self, node_id, write_freq):
        min_server = self.server_list[0]
        for server in self.server_list:
            if server.get_load() < min_server.get_load():
                min_server = server
        self._add_node_to_server(node_id=node_id, node_type=Constant.PRIMARY_COPY, write_freq=write_freq,
                                 server=min_server)

    def _add_node_to_server(self, node_id, node_type, write_freq, server):
        new_node = Node(id=node_id)
        self.node_list.append(new_node)
        new_node.server = server
        server.add_node(node_id=node_id, node_type=node_type, write_freq=write_freq)
        new_node.assign_virtual_primary_copy(server_list=self.server_list)
        adj_node_list = self.network_dataset.get_all_adj_node_id_list(node_id=node_id)
        for adj_node in adj_node_list:
            self.check_node_locality(node_id=node_id, adj_node_id=adj_node, meet_flag=True)

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

    def check_node_locality(self, node_id, adj_node_id, meet_flag=False):
        node = self.get_node_with_id(node_id=node_id)
        adj_node = self.get_node_with_id(node_id=adj_node_id)
        if node is None or adj_node is None or (
                node.server.has_node(node_id=adj_node_id) and adj_node.server.has_node(node_id=node_id)):
            return True
        else:
            if meet_flag is True:
                if not node.server.has_node(adj_node_id):
                    adj_node.add_non_primary_copy(node.server)
                if not adj_node.server.has_node(node_id):
                    node.add_non_primary_copy(adj_node.server)
                assert node.server.has_node(node_id=adj_node_id) and adj_node.server.has_node(node_id=node_id)
                return True
            else:
                return False

    def get_node_with_id(self, node_id):
        node = filter(lambda x: x.id == node_id, self.node_list)
        for node_i in node:
            return node_i

    # def get_relation_with_node(self, source_node_id, target_node_id):
    #     # TODO
    #     return -1

    def is_ssn_with(self, source_node_id, target_node_id):
        s_node = self.get_node_with_id(node_id=source_node_id)
        t_node = self.get_node_with_id(node_id=target_node_id)
        if s_node.server.id == t_node.server.id and self.network_dataset.has_edge(s_node_id=source_node_id,
                                                                                  t_node_id=target_node_id):
            return True
        else:
            return False

    def is_pssn_with(self, source_node_id, target_node_id):
        if not self.is_ssn_with(source_node_id, target_node_id):
            return False
        else:
            node_list = self.network_dataset.get_all_adj_node_id_list(node_id=source_node_id)
            for node_i in node_list:
                if not self.is_ssn_with(source_node_id, node_i):
                    return False
            return True

    def is_dns_with(self, source_node_id, target_node_id):
        s_node = self.get_node_with_id(node_id=source_node_id)
        t_node = self.get_node_with_id(node_id=target_node_id)
        if s_node.server.id != t_node.server.id and self.network_dataset.has_edge(s_node_id=source_node_id,
                                                                                  t_node_id=target_node_id):
            return True
        else:
            return False

    def is_pdsn_with(self, source_node_id, target_node_id):
        if not self.is_dns_with(source_node_id, target_node_id):
            return False
        else:
            source_node_adj_list = self.network_dataset.get_all_adj_node_id_list(node_id=source_node_id)
            target_node = self.get_node_with_id(target_node_id)

            for node_i in source_node_adj_list:
                if self.get_node_with_id(
                        node_id=node_i).server.id == target_node.server.id and node_i != target_node_id:
                    return False
            return False

    def compute_inter_server_cost(self):
        return compute_inter_sever_cost(servers=self.server_list)

    def node_bonus_on_server(self, node_id, server_id):
        adj_node_list = self.network_dataset.get_all_adj_node_id_list(node_id=node_id)
        for adj_node in adj_node_list:
            if self.get_node_with_id(node_id=adj_node).server.id == server_id and self.is_dns_with(
                    source_node_id=node_id, target_node_id=adj_node):
                return 1
        return 0

    def node_penalty_on_server(self, node_id, server_id):
        adj_node_list = self.network_dataset.get_all_adj_node_id_list(node_id=node_id)
        for adj_node in adj_node_list:
            if self.get_node_with_id(node_id=adj_node).server.id == server_id and self.is_ssn_with(
                    source_node_id=node_id, target_node_id=adj_node):
                return 1
        return 0

    def compute_scb(self, node_id, target_server_id):
        pass
