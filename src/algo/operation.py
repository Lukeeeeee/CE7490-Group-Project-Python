from src.core import Basic
from src.constant import Constant
from src.node.node import Node
from src.algo.inter_server_cost import compute_inter_sever_cost
import networkx as nx


class Operation(Basic):
    def __init__(self):
        super().__init__()

    @staticmethod
    def move_node_to_server(node, target_server, algo):
        adj_node_list = algo.network_dataset.get_all_adj_node_id_list(node_id=node.id)
        # CHECK ALL ADJ NODE WHETHER REMOVE REPLICA ON ORIGINAL SERVER (degree == 1)
        for adj_node_id in adj_node_list:
            if len(algo.network_dataset.get_all_adj_node_id_list(node_id=adj_node_id)) == 1 and node.server.has_node(
                    node_id=adj_node_id, node_type=Constant.NON_PRIMARY_COPY):
                Operation.remove_node_from_server(node_id=adj_node_id, server=node.server, algo=algo)
        node.server.remove_node(node_id=node.id, node_type=Constant.PRIMARY_COPY)
        if target_server.has_node(node_id=node.id):
            target_server_node_type = target_server.graph.nodes[node.id]['node_type']
            target_server.remove_node(node_id=node.id)
            # If target server has virtual primary copy, do add a new virtual primary copy in original server of node
            if target_server_node_type == Constant.VIRTUAL_PRIMARY_COPY:
                node.server.add_node(node_id=node.id, node_type=Constant.VIRTUAL_PRIMARY_COPY,
                                     write_freq=Constant.WRITE_FREQ)
        target_server.add_node(node_id=node.id, node_type=Constant.PRIMARY_COPY, write_freq=Constant.WRITE_FREQ)
        node.server = target_server
        Operation.remove_redundant_replica_of_node(node=node,
                                                   algo=algo)

        Operation._check_node_locality_with_all_adj_node(node=node,
                                                         algo=algo,
                                                         meet_flag=True)

    @staticmethod
    def remove_redundant_replica_on_server(server, algo):
        # TODO
        non_primary_copy_list = server.return_type_nodes(node_type=Constant.NON_PRIMARY_COPY)
        for node_id in non_primary_copy_list:
            pass
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
    def remove_node_from_server(node_id, server, algo):
        node = algo.get_node_with_id(node_id)
        node_type = server.graph.nodes[node_id]['node_type']
        if node_type == Constant.NON_PRIMARY_COPY:
            node.non_primary_copy_server_list.remove(server)
        elif node_type == Constant.VIRTUAL_PRIMARY_COPY:
            node.virtual_primary_copy_server_list.remove(server)
        server.remove_node(node_id=node_id)

    @staticmethod
    def has_adj_node_server_id(node, server, algo, adj_node_type=None):
        adj_node_list = algo.network_dataset.get_all_adj_node_id_list(node_id=node.id)
        for adj_node_i in adj_node_list:
            if server.graph.has_node(node_id=adj_node_i):
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
    def swap_virtual_primary_copy(s_node, t_node, s_server, t_server):
        try:
            s_node.virtual_primary_copy_server_list.remove(s_server)
            s_server.remove_node(node_id=s_node.id)
            s_node.add_virtual_primary_copy(target_server=t_server)

            t_node.virtual_primary_copy_server_list.remove(t_server)
            t_server.remove_node(node_id=t_node.id)
            t_node.add_virtual_primary_copy(target_server=s_server)
            print(
                "Swap virtual copy, node %d to server %d, node %d to server %d" %
                (s_node.id, t_server.id, t_node.id, s_server.id))
            return True
        except nx.NetworkXError:
            return False

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
