from src.core import Basic
from src.constant import Constant
from src.node.node import Node
from src.algo.inter_server_cost import compute_inter_sever_cost
import networkx as nx
import logging
import glob


class Operation(Basic):
    def __init__(self):
        super().__init__()

    @staticmethod
    def move_node_to_server(node, target_server, algo):
        log_str = "node %d moved to server %d" % (node.id, target_server.id)
        logging.info(log_str)
        print(log_str)
        adj_node_list = algo.network_dataset.get_all_adj_node_id_list(node_id=node.id)
        # CHECK ALL ADJ NODE WHETHER REMOVE REPLICA ON ORIGINAL SERVER (degree == 1)
        for adj_node_id in adj_node_list:
            if len(algo.network_dataset.get_all_adj_node_id_list(node_id=adj_node_id)) == 1 and node.server.has_node(
                    node_id=adj_node_id, node_type=Constant.NON_PRIMARY_COPY):
                Operation.remove_node_from_server(node_id=adj_node_id, server=node.server, algo=algo)
        Operation.remove_node_from_server(node_id=node.id, server=node.server, algo=algo)
        if target_server.has_node(node_id=node.id):
            target_server_node_type = target_server.graph.nodes[node.id]['node_type']
            Operation.remove_node_from_server(node_id=node.id, server=target_server, algo=algo)
            # If target server has virtual primary copy, do add a new virtual primary copy in original server of node
            if target_server_node_type == Constant.VIRTUAL_PRIMARY_COPY:
                node.add_virtual_primary_copy(target_server=node.server)
        target_server.add_node(node_id=node.id, node_type=Constant.PRIMARY_COPY, write_freq=Constant.WRITE_FREQ)
        node.server = target_server
        Operation.remove_redundant_replica_of_node(node=node,
                                                   algo=algo)

        Operation._check_node_locality_with_all_adj_node(node=node,
                                                         algo=algo,
                                                         meet_flag=True)

    @staticmethod
    def remove_redundant_replica_on_server(server, algo):
        raise NotImplementedError

    @staticmethod
    def _non_primary_copy_is_redundant(node, non_primary_copy_server, algo):
        if Operation.count_adj_node_server_id(node=node,
                                              server=non_primary_copy_server,
                                              algo=algo,
                                              adj_node_type=Constant.PRIMARY_COPY) == 0 and \
                non_primary_copy_server.has_node(node_id=node.id, node_type=Constant.NON_PRIMARY_COPY) is True:
            return True
        else:
            return False

    @staticmethod
    def _virtual_primary_copy_is_redundant():
        # TODO
        raise NotImplementedError
        pass

    @staticmethod
    def add_node_to_server(node_id, node_type, write_freq, server, algo):
        if node_type == Constant.PRIMARY_COPY:
            return Operation._add_new_primary_copy_node_to_server(node_id=node_id,
                                                                  write_freq=write_freq,
                                                                  server=server,
                                                                  algo=algo)
        else:
            server.add_node(node_id=node_id, node_type=node_type, write_freq=write_freq)
            return True

    @staticmethod
    def _check_node_locality_with_all_adj_node(node, algo, meet_flag):
        adj_node_list = algo.network_dataset.get_all_adj_node_id_list(node_id=node.id)
        for adj_node in adj_node_list:
            if not Operation.check_node_locality(node=node,
                                                 adj_node=algo.get_node_with_id(adj_node),
                                                 algo=algo,
                                                 meet_flag=meet_flag):
                raise ValueError('Locality not meet')
        return True

    @staticmethod
    def _add_new_primary_copy_node_to_server(node_id, write_freq, server, algo):
        new_node = Node(id=node_id)
        algo.node_list.append(new_node)
        algo.node_index_list[node_id] = len(algo.node_list) - 1
        new_node.server = server
        server.add_node(node_id=node_id, node_type=Constant.PRIMARY_COPY, write_freq=write_freq)
        new_node.assign_virtual_primary_copy(server_list=algo.server_list)
        Operation._check_node_locality_with_all_adj_node(node=new_node,
                                                         algo=algo,
                                                         meet_flag=True)
        return True

    @staticmethod
    def check_node_locality(node, adj_node, algo, meet_flag=False):
        if node is None or adj_node is None or (
                node.server.has_node(node_id=adj_node.id) and adj_node.server.has_node(node_id=node.id)):
            return True
        else:
            if meet_flag is True:
                if not node.server.has_node(adj_node.id):
                    adj_node.add_non_primary_copy(node.server)
                if not adj_node.server.has_node(node.id):
                    node.add_non_primary_copy(adj_node.server)
                assert node.server.has_node(node_id=adj_node.id) and \
                       adj_node.server.has_node(node_id=node.id)
                return True
            else:
                return False

    @staticmethod
    def delete_node(node, algo):
        for server in node.non_primary_copy_server_list:
            if server.has_node(node_id=node.id):
                server.remove_node(node_id=node.id)
        for server in node.virtual_primary_copy_server_list:
            if server.has_node(node_id=node.id):
                server.remove_node(node_id=node.id)
        algo.network_dataset.grah.remove_node(node.id)

    @staticmethod
    def remove_node_from_server(node_id, server, algo, req_node_type=None):
        node = algo.get_node_with_id(node_id)
        node_type = server.graph.nodes[node_id]['node_type']
        if req_node_type:
            assert req_node_type == node_type
        if node_type == Constant.NON_PRIMARY_COPY:
            node.non_primary_copy_server_list.remove(server)
        elif node_type == Constant.VIRTUAL_PRIMARY_COPY:
            node.virtual_primary_copy_server_list.remove(server)
        server.remove_node(node_id=node_id)

    @staticmethod
    def has_adj_node_server_id(node, server, algo, adj_node_type=None):
        adj_node_list = algo.network_dataset.get_all_adj_node_id_list(node_id=node.id)
        for adj_node_i in adj_node_list:
            if server.graph.has_node(adj_node_i):
                if adj_node_type and server.graph.nodes[adj_node_i]['node_type'] == adj_node_type:
                    return True
        return False

    @staticmethod
    def count_adj_node_server_id(node, server, algo, adj_node_type=None):
        count = 0
        adj_node_list = algo.network_dataset.get_all_adj_node_id_list(node_id=node.id)
        for adj_node_i in adj_node_list:
            if server.has_node(node_id=adj_node_i, node_type=adj_node_type):
                count += 1
        return count

    @staticmethod
    def swap_virtual_primary_copy(s_node, t_node, s_server, t_server, algo):
        Operation.remove_node_from_server(node_id=s_node.id, server=s_server, algo=algo,
                                          req_node_type=Constant.VIRTUAL_PRIMARY_COPY)
        if t_server.has_node(node_id=s_node.id, node_type=Constant.NON_PRIMARY_COPY):
            Operation.remove_node_from_server(node_id=s_node.id, server=t_server, algo=algo,
                                              req_node_type=Constant.NON_PRIMARY_COPY)

        Operation.remove_node_from_server(node_id=t_node.id, server=t_server, algo=algo,
                                          req_node_type=Constant.VIRTUAL_PRIMARY_COPY)
        if s_server.has_node(node_id=t_node.id, node_type=Constant.NON_PRIMARY_COPY):
            Operation.remove_node_from_server(node_id=t_node.id, server=s_server, algo=algo,
                                              req_node_type=Constant.NON_PRIMARY_COPY)

        s_node.add_virtual_primary_copy(target_server=t_server)
        t_node.add_virtual_primary_copy(target_server=s_server)

        log_str = "Swap virtual copy, node %d to server %d, node %d to server %d" % (
            s_node.id, t_server.id, t_node.id, s_server.id)
        logging.info(log_str)
        print(log_str)
        return True

    @staticmethod
    def move_merged_node(merged_node, target_server, algo):
        for node in merged_node.node_list:
            Operation.move_node_to_server(node=node,
                                          target_server=target_server,
                                          algo=algo)
        merged_node.server = target_server

    @staticmethod
    def remove_redundant_replica_of_node(node, algo):
        for server in algo.server_list:
            # If node has no connected with node that its primary copy on server,
            # but the node has a non primary copy on server to meet locality, remove it.
            if Operation._non_primary_copy_is_redundant(node=node,
                                                        non_primary_copy_server=server,
                                                        algo=algo) is True:
                server.remove_node(node_id=node.id)
                for server_i in node.non_primary_copy_server_list:
                    if server.id == server_i.id:
                        node.non_primary_copy_server_list.remove(server_i)
        while len(node.virtual_primary_copy_server_list) > Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER:
            node.virtual_primary_copy_server_list[-1].remove_node(node_id=node.id)
            node.virtual_primary_copy_server_list.pop()

    @staticmethod
    def validate_result(dataset_g, server_g_list, load_differ=1, virtual_copy_numer=2):
        node_list = list(dataset_g.nodes)
        vir_copy = [0 for _ in range(max(node_list) + 1)]
        non_copy = [0 for _ in range(max(node_list) + 1)]
        pr_copy = [0 for _ in range(max(node_list) + 1)]
        max_load = -1
        min_load = 1000000
        global_flag = True
        for server in server_g_list:
            load = 0
            for node in list(server.nodes):
                if server.nodes[node]['node_type'] == Constant.VIRTUAL_PRIMARY_COPY:
                    vir_copy[node] += 1
                    load += 1
                elif server.nodes[node]['node_type'] == Constant.NON_PRIMARY_COPY:
                    non_copy[node] += 1
                elif server.nodes[node]['node_type'] == Constant.PRIMARY_COPY:
                    load += 1
                    pr_copy[node] += 1
            max_load = max(max_load, load)
            min_load = min(min_load, load)
        log_str = "Min load %d, Max load %d, Load max differ is %d" % (min_load, max_load, abs(max_load - min_load))
        logging.info(log_str)
        print(log_str)

        # Check load balance
        if abs(max_load - min_load) > load_differ:
            log_str = 'Load balance is not met !!!'
            print(log_str)
            logging.error(log_str)
            global_flag = False
        else:
            log_str = 'Load balance is met'
            print(log_str)
            logging.info(log_str)
        # Check virtual primary copy number
        for node in list(dataset_g.nodes):
            if vir_copy[node] == virtual_copy_numer:
                res = False
            else:
                res = True
            if res is True:
                log_str = "Node %d virtual primary copy number is %d, constraint is met" % (node, vir_copy[node])
                logging.info(log_str)
                print(log_str)
            else:
                log_str = "Node %d virtual primary copy number is %d, constraint is not met!!!" % (node, vir_copy[node])
                logging.error(log_str)
                print(log_str)
                global_flag = False

        # Check locality
        for server in server_g_list:
            for node in list(server.nodes):
                if server.nodes[node]['node_type'] == Constant.PRIMARY_COPY:
                    met_flag = True
                    for adj_node in list(dataset_g[node]):
                        if not server.has_node(adj_node):
                            met_flag = False
                            log_str = "Node %d missed adj %d" % (node, adj_node)
                            logging.error(log_str)
                            print(log_str)
                            global_flag = False
                    if met_flag:
                        log_str = "Node %d met locality" % (node)
                        logging.info(log_str)
                        print(log_str)
        # Check only one primary copy
        for node in list(dataset_g.nodes):
            if pr_copy[node] == 1:
                log_str = "Node %d only have one primary copy" % node
                logging.info(log_str)
                print(log_str)
            else:
                log_str = "Node %d have %d primary copy!!!" % (node, pr_copy[node])
                logging.error(log_str)
                print(log_str)
                global_flag = False
        if global_flag is False:
            log_str = 'Overall constraint is not met!!!!!'
            logging.error(log_str)
            print(log_str)
        else:
            log_str = 'Overall constraint is met'
            logging.info(log_str)
            print(log_str)

    @staticmethod
    def load_log(log_path):
        dataset_g = nx.read_gpickle(log_path + '/dataset_graph.gpickle')
        server_g_list = []
        server_f_list = glob.glob(log_path + '/server_*.gpickle')
        for f in server_f_list:
            server_g_list.append(nx.read_gpickle(f))
        log_str = 'read the log'
        logging.info(log_str)
        print(log_str)
        return dataset_g, server_g_list


if __name__ == '__main__':
    dataset, server = Operation.load_log(
        log_path='/home/dls/meng/CE7490-Group-Project-Python/log/2018-10-26_13-24-19_offline_amazons_0.01_debug')
    Operation.validate_result(dataset, server)
