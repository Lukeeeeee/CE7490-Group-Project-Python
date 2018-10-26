from src.core import Basic
from src.constant import Constant
from src.node.node import Node
from src.algo.inter_server_cost import compute_inter_sever_cost
from src.algo.operation import Operation
from src.algo.algo import Algo
import numpy as np
from src.node.mergedNode import MergedNode
import logging


class OfflineAlgo(Algo):
    def __init__(self, server_list, network_dataset):
        super().__init__(server_list=server_list, network_dataset=network_dataset)
        self.server_list = server_list
        for i in range(len(self.server_list)):
            assert self.server_list[i].id == i

        self.network_dataset = network_dataset
        max_node_id = max(list(self.network_dataset.graph.nodes))
        self.node_list = []
        self.merged_node_list = []
        self.node_index_list = [-1 for _ in range(max_node_id + 1)]

    def add_new_primary_node(self, node_id, write_freq):
        min_server = self.get_min_load_server()
        self._add_node_to_server(node_id=node_id, node_type=Constant.PRIMARY_COPY, write_freq=write_freq,
                                 server=min_server)
        self._one_node_relocation_process(node=self.get_node_with_id(node_id=node_id))

    def _add_node_to_server(self, node_id, node_type, write_freq, server):
        Operation.add_node_to_server(node_id=node_id,
                                     node_type=node_type,
                                     write_freq=write_freq,
                                     server=server,
                                     algo=self)

    def get_min_load_server(self):
        min_server = self.server_list[0]
        for server in self.server_list:
            if server.get_load() < min_server.get_load():
                min_server = server
        return min_server

    def get_max_load_server(self):
        max_server = self.server_list[0]
        for server in self.server_list:
            if server.get_load() > max_server.get_load():
                max_server = server
        return max_server

    # def get_primary_copy_server(self, node_id):
    #     res = None
    #     for server in self.server_list:
    #         pr_node = server.get_node(node_id=node_id)
    #         if not pr_node and pr_node['NODE_TYPE'] == Constant.PRIMARY_COPY:
    #             if res is not None:
    #                 logging.error("Multiple primary copy existed")
    #                 raise RuntimeError("Multiple primary copy existed")
    #             res = server
    #             break
    #     return res

    # def check_node_locality(self, node_id, adj_node_id, meet_flag=False):
    #
    #     Operation.check_node_locality(node=self.get_node_with_id(node_id),
    #                                   adj_node=self.get_node_with_id(adj_node_id),
    #                                   meet_flag=meet_flag,
    #                                   algo=self)

    def get_node_with_id(self, node_id):
        # import bisect
        # res = bisect.bisect(self.node_list, node)
        # node = list(filter(lambda x: x.id == node_id, self.node_list))
        # assert len(node) <= 1
        # for node_i in node:
        #     return node_i
        if self.node_index_list[node_id] == -1:
            return None
        else:
            res = self.node_list[self.node_index_list[node_id]]
            assert res.id == node_id
            return res

    def get_merged_node_with_id(self, node_id):
        node = self.get_node_with_id(node_id=node_id)
        merged_node = list(filter(lambda x: x.id == node.merged_node_id, self.merged_node_list))
        assert len(merged_node) <= 1
        for node in merged_node:
            return node
        return None

    def get_server_with_id(self, server_id):
        return self.server_list[server_id]

    # def get_relation_with_node(self, source_node_id, target_node_id):
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
                if self.get_node_with_id(node_id=node_i) and \
                        self.get_node_with_id(
                            node_id=node_i).server.id == target_node.server.id and node_i != target_node_id:
                    return False
            return True

    def compute_inter_server_cost(self):
        return compute_inter_sever_cost(servers=self.server_list)

    def node_bonus_on_server(self, node_id, server_id):
        adj_node_list = self.network_dataset.get_all_adj_node_id_list(node_id=node_id)
        for adj_node in adj_node_list:
            if self.get_node_with_id(node_id=adj_node) and \
                    self.get_node_with_id(node_id=adj_node).server.id == server_id and self.is_dsn_with(
                source_node_id=node_id, target_node_id=adj_node):
                # TODO the bonus do is a two-value 1 or 0
                return 1
        return 0

    def node_penalty_on_server(self, node_id, server_id):
        adj_node_list = self.network_dataset.get_all_adj_node_id_list(node_id=node_id)
        for adj_node in adj_node_list:
            if self.get_node_with_id(node_id=adj_node) and self.get_node_with_id(
                    node_id=adj_node).server.id == server_id and self.is_ssn_with(
                source_node_id=node_id, target_node_id=adj_node):
                return -1
        return 0

    def compute_scb(self, node_id, target_server_id):
        scb = 0
        # add PDSN_B
        node = self.get_node_with_id(node_id=node_id)
        assert node.server_id != target_server_id
        scb += self.get_certain_relation_node_count_with_servers(source_node_id=node_id,
                                                                 relation_func=self.is_pdsn_with,
                                                                 target_server_list=[target_server_id])
        # add PDSN_no_A_B
        tmp_server_list = list(range(len(self.server_list)))
        tmp_server_list.remove(node.server_id)
        tmp_server_list.remove(target_server_id)
        scb += self.get_certain_relation_node_count_with_servers(source_node_id=node_id,
                                                                 relation_func=self.is_pdsn_with,
                                                                 target_server_list=tmp_server_list)

        # minus pssn
        tmp_server_list = list(range(len(self.server_list)))
        tmp_server_list.remove(node.server_id)
        tmp_server_list.remove(target_server_id)
        scb -= self.get_certain_relation_node_count_with_servers(source_node_id=node_id,
                                                                 relation_func=self.is_pssn_with,
                                                                 target_server_list=tmp_server_list)

        # minus dsn
        tmp_server_list = list(range(len(self.server_list)))
        tmp_server_list.remove(node.server_id)
        tmp_server_list.remove(target_server_id)

        scb -= self.get_certain_relation_node_count_with_servers(source_node_id=node_id,
                                                                 relation_func=self.is_dsn_with,
                                                                 target_server_list=tmp_server_list)

        scb += self.node_bonus_on_server(node_id=node_id, server_id=target_server_id)

        scb += self.node_penalty_on_server(node_id=node_id, server_id=self.get_node_with_id(node_id=node_id).server.id)

        return scb

    def _certain_relation_node_count_in_server(self, source_node_id, target_server_id, relation_func):
        count = 0
        # TODO this can be done by Operation.count_adj_node_server_id()?
        adj_node_list = self.network_dataset.get_all_adj_node_id_list(node_id=source_node_id)
        for adj_node in adj_node_list:
            if self.get_node_with_id(node_id=adj_node) and self.get_node_with_id(
                    node_id=adj_node).server.id == target_server_id and relation_func(
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
                self._one_node_relocation_process(node)

    def _one_node_relocation_process(self, node):
        log_str = "Relocate change node %d" % node.id
        logging.info(log_str)
        print(log_str)
        pre_server_id = node.server.id
        if self.node_relocate(node=node) is True:
            log_str = "Node %d was relocated from %d to %d" % (node.id, pre_server_id, node.server.id)
            logging.info(log_str)
            print(log_str)

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
            if self._check_load_constraint_when_swap(source_server=node.server, target_server=final_new_server):
                Operation.move_node_to_server(node=node, target_server=final_new_server, algo=self)
                return True
            else:
                log_str = "Node relocate change to swap "
                print(log_str)
                logging.info(log_str)
                assert final_new_server.id != node.server_id
                return self.swap_node_on_server(node=node, target_server=final_new_server, scb=max_scb)
        else:
            return False

    def _check_load_constraint_when_swap(self, source_server, target_server):
        if abs(target_server.get_load() + 1 - (
                source_server.get_load() - 1)) > Constant.MAX_LOAD_DIFFERENCE_AMONG_SERVER:
            return False
        if self.get_min_load_server().id != target_server.id and \
                abs(target_server.get_load() + 1 - (
                self.get_min_load_server().get_load())) > Constant.MAX_LOAD_DIFFERENCE_AMONG_SERVER:
            return False

        return True

    def swap_node_on_server(self, node, target_server, scb):
        adj_node_list = self.network_dataset.get_all_adj_node_id_list(node_id=node.id)
        swap_flag = False

        for adj_node_i in adj_node_list:
            adj_node = self.get_node_with_id(node_id=adj_node_i)
            if not adj_node:
                continue
            else:
                if adj_node.server.id == target_server.id:
                    if self.compute_scb(node_id=adj_node_i, target_server_id=node.server.id) + scb > 0:
                        pre_server_id = node.server.id

                        Operation.move_node_to_server(node=node, target_server=target_server, algo=self)
                        Operation.move_node_to_server(adj_node, target_server=self.get_server_with_id(pre_server_id),
                                                      algo=self)
                        swap_flag = True
                        break
        if swap_flag:
            Operation.remove_redundant_replica_of_node(node=node, algo=self)
        return swap_flag

    def init_merge_process(self):
        node_rand_index = np.arange(len(self.node_list))
        np.random.shuffle(node_rand_index)
        for index in node_rand_index:
            node = self.node_list[index]
            merge_node = MergedNode(ID=node.id, server=node.server, node=node, algo=self)
            self.merged_node_list.append(merge_node)

    def start_merge_process(self):
        node_rand_index = np.arange(len(self.merged_node_list))
        np.random.shuffle(node_rand_index)
        for index in node_rand_index:
            while index >= len(self.merged_node_list):
                index = np.random.randint(0, len(self.merged_node_list))
            merged_node = self.merged_node_list[index]
            merged_node.launch_merge_node_process(algo=self)

    def init_group_swap_process(self):
        # Get two random group
        # Compute the replica will decrease or not after swapped
        # Also check the data availability (i.e. the number of virtual primary copy)
        # Use loose constraint, if the one of the server became unbalanced, after merged, just migrated node from high
        # to low load server
        self.merged_node_list.sort(key=lambda x: x.node_count, reverse=True)
        for i in range(len(self.merged_node_list) - 1):
            for j in range(i + 1, len(self.merged_node_list)):
                if abs(self.merged_node_list[i].node_count - self.merged_node_list[j].node_count) > \
                        Constant.MERGED_GROUP_LOOSE_CONSTRAINT_EPSILON or \
                        self._compute_gain_in_swap_merged_node_process(s_merged_node=self.merged_node_list[i],
                                                                       t_merged_node=self.merged_node_list[j]) < 0:
                    break
                else:
                    tmp_i_server = self.merged_node_list[i].server
                    Operation.move_merged_node(merged_node=self.merged_node_list[i],
                                               target_server=self.merged_node_list[j].server,
                                               algo=self)
                    Operation.move_merged_node(merged_node=self.merged_node_list[j],
                                               target_server=tmp_i_server,
                                               algo=self)

    def virtual_primary_copy_swap(self):
        # Random choose two virtual primary copy
        # if swapped resulted into eliminating the non-primary copy, then swap
        for node in self.node_list:
            for vir_pr_server in node.virtual_primary_copy_server_list:
                swapped_flag = False
                for non_pr_server in node.non_primary_copy_server_list:
                    non_pr_node_list = vir_pr_server.return_type_nodes(
                        node_type=Constant.NON_PRIMARY_COPY)
                    vir_pr_node_list = non_pr_server.return_type_nodes(
                        node_type=Constant.VIRTUAL_PRIMARY_COPY)

                    satisfied_node_list = list(set(non_pr_node_list) & set(vir_pr_node_list))
                    for t_node in satisfied_node_list:
                        if Operation.swap_virtual_primary_copy(s_node=node,
                                                               t_node=self.get_node_with_id(t_node),
                                                               s_server=vir_pr_server,
                                                               t_server=non_pr_server,
                                                               algo=self) is True:
                            swapped_flag = True
                            break
                    if swapped_flag is True:
                        break
                if swapped_flag is True:
                    break

    def _compute_gain_in_swap_merged_node_process(self, s_merged_node, t_merged_node):
        s_server = s_merged_node.server
        t_server = t_merged_node.server
        gain = 0
        for node in s_merged_node.node_list:
            gain += self._compute_gain_in_swap_merge_node_process_of_node(node=node,
                                                                          s_merged_node=s_merged_node,
                                                                          t_merged_node=t_merged_node,
                                                                          s_server=s_server,
                                                                          t_server=t_server)
        for node in t_merged_node.node_list:
            gain += self._compute_gain_in_swap_merge_node_process_of_node(node=node,
                                                                          s_merged_node=t_merged_node,
                                                                          t_merged_node=s_merged_node,
                                                                          s_server=t_server,
                                                                          t_server=s_server)

        return gain

    def _compute_gain_in_swap_merge_node_process_of_node(self, node, s_merged_node, t_merged_node, s_server, t_server):
        reduced_replica = 0

        for rest_node_id in s_server.primary_copy_node_list:
            # count the replicas need to be created after move to t server
            if rest_node_id not in s_merged_node.node_id_list and \
                    self.network_dataset.has_edge(node.id, rest_node_id):
                reduced_replica -= 1
        adj_node_id_list = self.network_dataset.get_all_adj_node_id_list(node_id=node.id)
        for adj_node_id in adj_node_id_list:
            # count the replicas that can be removed after move to t server,
            # the adj node's primary copy need to be at t server,
            # and have only one adj node which is node in s server
            # then its replica can be removed
            if adj_node_id in t_server.primary_copy_node_list and \
                    Operation.count_adj_node_server_id(node=self.get_node_with_id(node_id=adj_node_id),
                                                       server=s_server,
                                                       adj_node_type=Constant.PRIMARY_COPY,
                                                       algo=self) == 1:
                reduced_replica += 1
        return reduced_replica
