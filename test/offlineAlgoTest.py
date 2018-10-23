import os
import sys

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(CURRENT_PATH)
PAR_PATH = os.path.abspath(os.path.join(CURRENT_PATH, os.pardir))
sys.path.append(PAR_PATH)

from src.algo.offlineAlgo import OfflineAlgo
import networkx as nx
from src.dataset import Dataset
from src.server.server import Server
from src.constant import Constant


def print_graph(server_list):
    for server in server_list:
        print("Server: %d, load: %d" % (server.id, server.get_load()))
        for node in server.graph.nodes:
            print(node, server.graph.nodes[node])


def main():
    data = Dataset(dataset_str='facebook')

    server_list = [Server(serer_id=i) for i in range(100)]
    algo = OfflineAlgo(server_list=server_list, network_dataset=data)
    node_list = list(data.graph.nodes)
    node_len = len(node_list)
    for i in range(node_len):
        n = node_list[i]
        print("(%d/%d) Adding node: " % (i, node_len), n)
        algo.add_new_primary_node(node_id=n, write_freq=Constant.WRITE_FREQ)
    # print_graph(server_list)
    print_graph(server_list)

    print(algo.compute_inter_server_cost())
    print("Running relocation process")
    algo.node_relocation_process()

    print("Running init merge process")
    algo.init_merge_process()
    print("Running node merge process")

    algo.start_merge_process()
    print("Running group swap process")

    algo.init_group_swap_process()
    print("Running virtual primary copy swap process")

    algo.virtual_primary_copy_swap()
    print_graph(server_list)
    print(algo.compute_inter_server_cost())


if __name__ == '__main__':
    main()
