import os
import sys

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(CURRENT_PATH)
PAR_PATH = os.path.abspath(os.path.join(CURRENT_PATH, os.pardir))
sys.path.append(PAR_PATH)
import logging
from log import LOG_PATH

from src.algo.offlineAlgo import OfflineAlgo
import networkx as nx
from src.dataset import Dataset
from src.server.server import Server
from src.constant import Constant
import time


def print_graph(server_list):
    for server in server_list:
        log_str = "Server: %d, load: %d" % (server.id, server.get_load())
        logging.info(log_str)
        print(log_str)
        for node in server.graph.nodes:
            log_str = "%d: node type %s, write freq %f" % (node, server.graph.nodes[node]['node_type'],
                                                           server.graph.nodes[node]['write_freq'])
            logging.info(log_str)
            print(log_str)


def main(dataset='amazon', part_flag=0.01):
    logging.basicConfig(level=logging.DEBUG,
                        filename=os.path.join(LOG_PATH, '%s_%s_%s_%s' % (
                            time.strftime("%Y-%m-%d_%H-%M-%S"), 'offline', dataset, str(part_flag))),
                        filemode='w')
    Constant().log_out()
    data = Dataset(dataset_str=dataset, part_flag=part_flag)

    server_list = [Server(serer_id=i) for i in range(Constant.SERVER_NUMBER)]
    algo = OfflineAlgo(server_list=server_list, network_dataset=data)
    node_list = list(data.graph.nodes)
    node_len = len(node_list)
    for i in range(node_len):
        n = node_list[i]
        log_str = "(%d/%d) Adding node: %d" % (i, node_len, n)
        logging.info(log_str)
        print(log_str)
        algo.add_new_primary_node(node_id=n, write_freq=Constant.WRITE_FREQ)
    # print_graph(server_list)
    print_graph(server_list)

    log_str = 'Inter Server cost is %f' % algo.compute_inter_server_cost()
    print(log_str)
    logging.info(log_str)

    print("Running relocation process")
    logging.info("Running relocation process")
    algo.node_relocation_process()

    log_str = 'Inter Server cost is %f' % algo.compute_inter_server_cost()
    print(log_str)
    logging.info(log_str)

    print("Running init merge process")
    logging.info("Running init merge process")
    algo.init_merge_process()

    print("Running node merge process")
    logging.info("Running node merge process")
    algo.start_merge_process()

    log_str = 'Inter Server cost is %f' % algo.compute_inter_server_cost()
    print(log_str)
    logging.info(log_str)

    print("Running group swap process")
    logging.info("Running group swap process")
    algo.init_group_swap_process()

    print("Running virtual primary copy swap process")
    logging.info("Running virtual primary copy swap process")
    algo.virtual_primary_copy_swap()
    print_graph(server_list)
    print(algo.compute_inter_server_cost())


if __name__ == '__main__':
    main(dataset='p2pgnutella', part_flag=0.1)
