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
from src.algo.operation import Operation as op


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


def main(dataset='amazon', part_flag=0.01, log_path_end='', tmp_log_flag=False):
    log_path = LOG_PATH
    log_path = os.path.join(log_path, '%s_%s_%s_%s_%s' % (
        time.strftime("%Y-%m-%d_%H-%M-%S"), 'offline', dataset, str(part_flag), log_path_end))
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    logging.basicConfig(level=logging.DEBUG,
                        filename=log_path + '/log',
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
    print_graph(server_list)
    op.validate_result(dataset_g=algo.network_dataset.graph,
                       server_g_list=[x.graph for x in algo.server_list],
                       load_differ=Constant.MAX_LOAD_DIFFERENCE_AMONG_SERVER,
                       virtual_copy_numer=Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER)
    log_str = 'Inter Server cost is %f' % algo.compute_inter_server_cost()
    print(log_str)
    logging.info(log_str)

    print("Running relocation process-------------")
    logging.info("Running relocation process-------------")
    algo.node_relocation_process()
    log_str = 'Inter Server cost is %f' % algo.compute_inter_server_cost()
    print(log_str)
    logging.info(log_str)
    print_graph(server_list)
    op.validate_result(dataset_g=algo.network_dataset.graph,
                       server_g_list=[x.graph for x in algo.server_list],
                       load_differ=Constant.MAX_LOAD_DIFFERENCE_AMONG_SERVER,
                       virtual_copy_numer=Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER)
    print("Init merge process-------------")
    logging.info("Init merge process-------------")
    algo.init_merge_process()
    print_graph(server_list)
    op.validate_result(dataset_g=algo.network_dataset.graph,
                       server_g_list=[x.graph for x in algo.server_list],
                       load_differ=Constant.MAX_LOAD_DIFFERENCE_AMONG_SERVER,
                       virtual_copy_numer=Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER)
    print("Start merge process-------------")
    logging.info("Start merge process-------------")
    algo.start_merge_process()
    print_graph(server_list)
    log_str = 'Inter Server cost is %f' % algo.compute_inter_server_cost()
    print(log_str)
    logging.info(log_str)
    op.validate_result(dataset_g=algo.network_dataset.graph,
                       server_g_list=[x.graph for x in algo.server_list],
                       load_differ=Constant.MAX_LOAD_DIFFERENCE_AMONG_SERVER,
                       virtual_copy_numer=Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER)
    print("Init Group Swap process-------------")
    logging.info("Init Group Swap process-------------")
    algo.init_group_swap_process()
    print_graph(server_list)
    op.validate_result(dataset_g=algo.network_dataset.graph,
                       server_g_list=[x.graph for x in algo.server_list],
                       load_differ=Constant.MAX_LOAD_DIFFERENCE_AMONG_SERVER,
                       virtual_copy_numer=Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER)
    print("Virtual Swap Copy Swap process-------------")
    logging.info("Virtual Swap Copy Swap process-------------")
    algo.virtual_primary_copy_swap()
    print_graph(server_list)
    log_str = 'Inter Server cost is %f' % algo.compute_inter_server_cost()
    print(log_str)
    logging.info(log_str)
    op.validate_result(dataset_g=algo.network_dataset.graph,
                       server_g_list=[x.graph for x in algo.server_list],
                       load_differ=Constant.MAX_LOAD_DIFFERENCE_AMONG_SERVER,
                       virtual_copy_numer=Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER)
    algo.save_all(path=log_path)
    g, server = op.load_log(log_path)
    op.validate_result(dataset_g=g,
                       server_g_list=server,
                       load_differ=Constant.MAX_LOAD_DIFFERENCE_AMONG_SERVER,
                       virtual_copy_numer=Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER)
    log_str = 'Inter Server cost is %f' % algo.compute_inter_server_cost()
    print(log_str)
    logging.info(log_str)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


if __name__ == '__main__':
    dataset = ['twitters1', 'twitters2', 'amazons', 'p2pgnutella', 'facebook']
    # for str_d in dataset:
    #     main(dataset=str_d, part_flag=0.01, log_path_end='_v1', tmp_log_flag=True)
    # main(dataset='twitters1', part_flag=0.1, log_path_end='debug')
    # main(dataset='twitters2', part_flag=0.1, log_path_end='debug')

    # res = [2, 4, 6, 8]
    # for rr in res:
    #     Constant.SERVER_NUMBER = rr
    #     main(dataset='twitters2',
    #          part_flag=0.01,
    #          log_path_end='fig_3_server_%d_vir_copy_%d' % (Constant.SERVER_NUMBER, Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER))
    # main(dataset='p2pgnutella', part_flag=0.1, log_path_end='debug')
    # main(dataset='facebook', part_flag=0.1, log_path_end='debug')
    main(dataset='amazons',
         part_flag=0.01,
         # log_path_end='fig_9_server_%d_vir_copy_%d' % (Constant.SERVER_NUMBER, Constant.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER))
         log_path_end='debug')
