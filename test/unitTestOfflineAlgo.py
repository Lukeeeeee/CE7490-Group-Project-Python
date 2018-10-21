import unittest
import networkx as nx
from src.algo.offlineAlgo import OfflineAlgo
from src.dataset import Dataset
from src.server.server import Server
from src.constant import Constant
from src.algo.operation import Operation


def create_algo(server_count=4, node_count=10):
    data = Dataset(dataset_str='facebook')
    data.graph = nx.Graph()
    for i in range(node_count):
        data.graph.add_node(i)
    server_list = [Server(serer_id=i) for i in range(server_count)]
    algo = OfflineAlgo(server_list=server_list, network_dataset=data)
    return algo


class TestOfflineAlgo(unittest.TestCase):

    def test_basic_assign_new_node(self):
        algo = create_algo(node_count=4, server_count=10)
        algo.network_dataset.graph.add_edge(0, 1)
        algo._add_node_to_server(node_id=0, node_type=Constant.PRIMARY_COPY, write_freq=10.0,
                                 server=algo.server_list[0])
        algo._add_node_to_server(node_id=1, node_type=Constant.PRIMARY_COPY, write_freq=10.0,
                                 server=algo.server_list[1])
        self.assertTrue(algo.server_list[0].has_node(node_id=0, node_type=Constant.PRIMARY_COPY))
        self.assertTrue(algo.server_list[1].has_node(node_id=0, node_type=Constant.NON_PRIMARY_COPY) or
                        algo.server_list[1].has_node(node_id=0, node_type=Constant.VIRTUAL_PRIMARY_COPY))

        self.assertTrue(algo.server_list[1].has_node(node_id=1, node_type=Constant.PRIMARY_COPY))
        self.assertTrue(algo.server_list[0].has_node(node_id=1, node_type=Constant.NON_PRIMARY_COPY) or
                        algo.server_list[0].has_node(node_id=1, node_type=Constant.VIRTUAL_PRIMARY_COPY))

        algo.get_node_with_id(1).add_non_primary_copy(target_server=algo.server_list[9])
        self.assertTrue(algo.server_list[9].has_node(node_id=1, node_type=Constant.NON_PRIMARY_COPY))

        Operation.remove_redundant_replica_of_node(node=algo.get_node_with_id(1), algo=algo)
        self.assertFalse(algo.server_list[9].has_node(node_id=1, node_type=Constant.NON_PRIMARY_COPY))

    def test_node_relation_func(self):
        algo = create_algo()
        algo.network_dataset.graph.add_edge(0, 1)
        algo._add_node_to_server(node_id=0, node_type=Constant.PRIMARY_COPY, write_freq=10.0,
                                 server=algo.server_list[0])
        algo._add_node_to_server(node_id=1, node_type=Constant.PRIMARY_COPY, write_freq=10.0,
                                 server=algo.server_list[0])
        self.assertTrue(algo.is_ssn_with(0, 1))
        self.assertTrue(algo.is_ssn_with(1, 0))
        self.assertTrue(algo.is_pssn_with(0, 1))
        self.assertTrue(algo.is_pssn_with(1, 0))

        self.assertFalse(algo.is_pdsn_with(0, 1))
        self.assertFalse(algo.is_pdsn_with(1, 0))
        self.assertFalse(algo.is_dsn_with(0, 1))
        self.assertFalse(algo.is_dsn_with(1, 0))

        algo.network_dataset.graph.add_edge(0, 2)

        algo._add_node_to_server(node_id=2, node_type=Constant.PRIMARY_COPY, write_freq=10.0,
                                 server=algo.server_list[1])
        self.assertFalse(algo.is_ssn_with(0, 2))
        self.assertFalse(algo.is_ssn_with(2, 0))
        self.assertFalse(algo.is_pssn_with(0, 2))
        self.assertFalse(algo.is_pssn_with(2, 0))

        self.assertFalse(algo.is_pssn_with(0, 1))
        self.assertTrue(algo.is_pssn_with(1, 0))

        self.assertTrue(algo.is_dsn_with(0, 2))
        self.assertTrue(algo.is_dsn_with(2, 0))
        self.assertTrue(algo.is_pdsn_with(0, 2))
        self.assertTrue(algo.is_pdsn_with(2, 0))

    def test_node_move(self):
        algo = create_algo(server_count=2, node_count=10)
        algo.network_dataset.graph.add_edge(0, 1)
        algo._add_node_to_server(node_id=0, node_type=Constant.PRIMARY_COPY, write_freq=10.0,
                                 server=algo.server_list[0])
        algo._add_node_to_server(node_id=1, node_type=Constant.PRIMARY_COPY, write_freq=10.0,
                                 server=algo.server_list[1])
        self.assertTrue(algo.server_list[0].has_node(0, node_type=Constant.PRIMARY_COPY))
        self.assertTrue(algo.server_list[1].has_node(0, node_type=Constant.NON_PRIMARY_COPY) or
                        algo.server_list[1].has_node(0, node_type=Constant.VIRTUAL_PRIMARY_COPY))

        Operation.move_node_to_server(node=algo.get_node_with_id(0), target_server=algo.server_list[1], algo=algo)

        self.assertFalse(algo.server_list[0].has_node(0, node_type=Constant.PRIMARY_COPY))

        self.assertTrue(algo.server_list[1].has_node(0, node_type=Constant.PRIMARY_COPY))
        self.assertFalse(algo.server_list[1].has_node(0, node_type=Constant.NON_PRIMARY_COPY))
        self.assertFalse(algo.server_list[1].has_node(0, node_type=Constant.VIRTUAL_PRIMARY_COPY))


if __name__ == '__main__':
    unittest.main()
