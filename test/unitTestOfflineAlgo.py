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

    def test_relocate_process(self):
        data = Dataset(dataset_str='facebook')
        data.graph = nx.Graph()
        for i in range(10):
            data.graph.add_node(i)
        data.graph.add_edge(0, 1)
        data.graph.add_edge(0, 2)
        data.graph.add_edge(0, 3)
        data.graph.add_edge(0, 4)
        server_list = [Server(serer_id=i) for i in range(8)]
        algo = OfflineAlgo(server_list=server_list, network_dataset=data)
        node_list = list(data.graph.nodes)
        node_len = len(node_list)
        for i in range(node_len):
            n = node_list[i]
            algo.add_new_primary_node(node_id=n, write_freq=Constant.WRITE_FREQ)
        algo.node_relocation_process()
        self.assertEqual(algo.compute_inter_server_cost(), 0)

    def test_merge_process(self):
        data = Dataset(dataset_str='facebook')
        data.graph = nx.Graph()
        for i in range(10):
            data.graph.add_node(i)
        data.graph.add_edge(0, 1)
        data.graph.add_edge(0, 2)
        data.graph.add_edge(0, 3)
        data.graph.add_edge(0, 4)
        server_list = [Server(serer_id=i) for i in range(8)]
        algo = OfflineAlgo(server_list=server_list, network_dataset=data)
        node_list = list(data.graph.nodes)
        node_len = len(node_list)
        for i in range(node_len):
            n = node_list[i]
            algo.add_new_primary_node(node_id=n, write_freq=Constant.WRITE_FREQ)
        algo.init_merge_process()

        for i in range(0, len(algo.merged_node_list)):
            m_node = algo.merged_node_list[i]
            if m_node.id == 0:
                self.assertEqual(m_node.internal_connection, 0)
                self.assertEqual(m_node.external_connection, 4)
            elif m_node.id in [1, 2, 3, 4]:
                self.assertEqual(m_node.internal_connection, 0)
                self.assertEqual(m_node.external_connection, 1)
            else:
                self.assertEqual(m_node.internal_connection, 0)
                self.assertEqual(m_node.external_connection, 0)
        node_count_list = []
        for m_node in algo.merged_node_list:
            node_count_list += m_node.node_id_list
        node_count_list.sort()
        self.assertEqual(node_count_list, [i for i in range(10)])
        for i in range(1, len(algo.merged_node_list)):
            algo.merged_node_list[0]._add_node(algo.merged_node_list[i], algo=algo, remove_flag=False)
        node_count_list = algo.merged_node_list[0].node_id_list
        node_count_list.sort()
        self.assertEqual(node_count_list, [i for i in range(10)])
        self.assertEqual(algo.merged_node_list[0].external_connection, 0)
        self.assertEqual(algo.merged_node_list[0].internal_connection, 4)
        self.assertEqual(algo.merged_node_list[0].node_count, 10)


if __name__ == '__main__':
    unittest.main()
