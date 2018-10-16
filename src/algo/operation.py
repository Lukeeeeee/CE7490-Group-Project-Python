from src.core import Basic
from src.constant import Constant
from src.node.node import Node
from src.algo.inter_server_cost import compute_inter_sever_cost


class Operation(Basic):
    def __init__(self):
        super().__init__()

    @staticmethod
    def move_node_to_server(node, target_server, algo):
        pass

    @staticmethod
    def remove_redundant_replica(server, algo):
        pass

    @staticmethod
    def add_node_to_server(node_id, node_type, write_freq, server, algo):
        new_node = Node(id=node_id)
        algo.node_list.append(new_node)
        new_node.server = server
        server.add_node(node_id=node_id, node_type=node_type, write_freq=write_freq)
        new_node.assign_virtual_primary_copy(server_list=algo.server_list)
        adj_node_list = algo.network_dataset.get_all_adj_node_id_list(node_id=node_id)
        for adj_node in adj_node_list:
            Operation.check_node_locality(node=new_node,
                                          adj_node=algo.get_node_id(adj_node),
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
                assert node.server.has_node(node_id=adj_node.id) and adj_node.server.has_node(node_id=node.id)
                return True
            else:
                return False
