from src.core import Basic
from src.constant import Constant
from src.node.node import Node
from src.algo.inter_server_cost import compute_inter_sever_cost
from src.algo.operation import Operation
from src.algo.algo import Algo
import numpy as np
from src.node.mergedNode import MergedNode


class OfflineAlgo(Algo):
    def __init__(self, server_list, network_dataset):
        super().__init__(server_list=server_list, network_dataset=network_dataset)
        self.ETA = Constant.OFFLINE_ETA
        self.EPSILON = Constant.OFFLINE_EPSILON
        self.server_list = server_list
        self.network_dataset = network_dataset
        self.node_list = []
        self.merged_node_list = []

    def add_new_primary_node(self, node_id, write_freq):
        min_server = self.server_list[0]
        for server in self.server_list:
            if server.get_load() < min_server.get_load():
                min_server = server
        self._add_node_to_server(node_id=node_id, node_type=Constant.PRIMARY_COPY, write_freq=write_freq,
                                 server=min_server)

    def _add_node_to_server(self, node_id, node_type, write_freq, server):
        Operation.add_node_to_server(node_id=node_id,
                                     node_type=node_type,
                                     write_freq=write_freq,
                                     server=server,
                                     algo=self)

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

        Operation.check_node_locality(node=self.get_node_with_id(node_id),
                                      adj_node=self.get_node_with_id(adj_node_id),
                                      meet_flag=meet_flag,
                                      algo=self)

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

    def is_dsn_with(self, source_node_id, target_node_id):
        s_node = self.get_node_with_id(node_id=source_node_id)
        t_node = self.get_node_with_id(node_id=target_node_id)
        if s_node.server.id != t_node.server.id and self.network_dataset.has_edge(s_node_id=source_node_id,
                                                                                  t_node_id=target_node_id):
            return True
        else:
            return False

    def is_pdsn_with(self, source_node_id, target_node_id):
        if not self.is_dsn_with(source_node_id, target_node_id):
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
            if self.get_node_with_id(node_id=adj_node).server.id == server_id and self.is_dsn_with(
                    source_node_id=node_id, target_node_id=adj_node):
                # TODO the bonus do is a two-value 1 or 0
                return 1
        return 0

    def node_penalty_on_server(self, node_id, server_id):
        adj_node_list = self.network_dataset.get_all_adj_node_id_list(node_id=node_id)
        for adj_node in adj_node_list:
            if self.get_node_with_id(node_id=adj_node).server.id == server_id and self.is_ssn_with(
                    source_node_id=node_id, target_node_id=adj_node):
                return -1
        return 0

    def compute_scb(self, node_id, target_server_id):
        scb = 0
        # add PDSN_B
        scb += self.get_certain_relation_node_count_with_servers(source_node_id=node_id,
                                                                 relation_func=self.is_pdsn_with,
                                                                 target_server_list=[target_server_id])
        # add PDSN_no_A_B
        tmp_server_list = list(range(len(self.server_list)))
        tmp_server_list.remove(self.get_node_with_id(node_id).server_id)
        tmp_server_list.remove(target_server_id)
        scb += self.get_certain_relation_node_count_with_servers(source_node_id=node_id,
                                                                 relation_func=self.is_pdsn_with,
                                                                 target_server_list=tmp_server_list)

        # minus pssn
        tmp_server_list = list(range(len(self.server_list)))
        tmp_server_list.remove(self.get_node_with_id(node_id).server_id)
        tmp_server_list.remove(target_server_id)
        scb -= self.get_certain_relation_node_count_with_servers(source_node_id=node_id,
                                                                 relation_func=self.is_pssn_with,
                                                                 target_server_list=tmp_server_list)

        # minus dsn
        tmp_server_list = list(range(len(self.server_list)))
        tmp_server_list.remove(self.get_node_with_id(node_id).server_id)
        tmp_server_list.remove(target_server_id)

        scb -= self.get_certain_relation_node_count_with_servers(source_node_id=node_id,
                                                                 relation_func=self.is_dsn_with,
                                                                 target_server_list=tmp_server_list)

        scb += self.node_bonus_on_server(node_id=node_id, server_id=target_server_id)

        # TODO how to compute penalty
        scb += self.node_penalty_on_server(node_id=node_id, server_id=self.get_node_with_id(node_id=node_id).server.id)

        return scb

    def _certain_relation_node_count_in_server(self, source_node_id, target_server_id, relation_func):
        count = 0
        adj_node_list = self.network_dataset.get_all_adj_node_id_list(node_id=source_node_id)
        for adj_node in adj_node_list:
            if self.get_node_with_id(node_id=adj_node).server.id == target_server_id and relation_func(
                    source_node_id=source_node_id, target_node_id=adj_node):
                count += 1
        return count

    def get_certain_relation_node_count_with_servers(self, source_node_id, relation_func, target_server_list):
        # This func is used for computing scb
        count = 0
        for server in self.server_list:
            if server.id in target_server_list:
                count += self._certain_relation_node_count_in_server(source_node_id=source_node_id,
                                                                     target_server_id=server.id,
                                                                     relation_func=relation_func)
        return count

    def node_relocation_process(self, iteration_times=Constant.MAX_RELOCATE_ITERATION):
        for _ in range(iteration_times):
            for node in self.node_list:
                pre_server_id = node.server.id
                if self.node_relocate(node=node):
                    print("Node was relocated from %d to %d" % (pre_server_id, node.server.id))

    def node_relocate(self, node):
        max_scb = 0.0
        final_new_server = None
        for server_i in self.server_list:
            if node.server.id != server_i.id:
                scb = self.compute_scb(node_id=node.id, target_server_id=server_i.id)
                if scb > max_scb:
                    max_scb = scb
                    final_new_server = server_i
        if final_new_server:
            if abs(final_new_server.get_load() + 1 - (
                    node.server.get_load() - 1)) <= Constant.MAX_LOAD_DIFFERENCE_AMONG_SERER:
                Operation.move_node_to_server(node=node, target_server=final_new_server, algo=self)
            else:
                self.swap_node_on_server(node=node, target_server=final_new_server, scb=max_scb)
        else:
            return False

    def swap_node_on_server(self, node, target_server, scb):
        adj_node_list = self.network_dataset.get_all_adj_node_id_list(node_id=node.id)
        for adj_node_i in adj_node_list:
            adj_node = self.get_node_with_id(node_id=adj_node_i)
            if adj_node.server.id == target_server.id:
                if self.compute_scb(node_id=adj_node_i, target_server_id=node.server.id) + scb > 0:
                    Operation.move_node_to_server(node=node, target_server=target_server, algo=self)
                    Operation.move_node_to_server(adj_node, target_server=node.server, algo=self)
        Operation.remove_redundant_replica(server=target_server, algo=self)
        Operation.remove_redundant_replica(server=node.server, algo=self)

    def init_merge_process(self):
        rand_id = np.random.randint(0, len(self.node_list))
        merge_node = MergedNode(ID=0)
        merge_node.add_node(node=self.node_list[rand_id], dataset_graph=self.network_dataset)
