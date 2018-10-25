import numpy as np
import networkx as nx
import time
import logging
import pickle
from tqdm import tqdm
from src.algo.baselines.SPAR.read_data import read_file_to_dict
from src.algo.baselines.SPAR.Spar import Spar
from dataset import DATASET_PATH
from graphs.spar import SPAR_GRAPH_SAVE_PATH
from log import LOG_PATH
from src.constant import Constant


def save_obj(obj, name, path):
    with open(path + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name, path):
    with open(path + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def spar_inter_server_cost(slave_dict):
    cost = 0
    for server, replicas in slave_dict.items():
        cost += len(replicas)

    return cost


def calculate_mean_length(dict):
    length = 0
    iter = 0
    for key, data in dict.items():
        length += len(data)
        iter += 1
    return int(length/iter)


def test_spar_sample(file, server_number, minimum_replicas, percent10_stop, path):
    filename = DATASET_PATH + '/' + file + '.txt'
    # path = '././dataset/'
    # filename = path + file + '.txt'

    node_list, node_neighbor_dic, col_data = read_file_to_dict(filename)

    node_num = 0
    start_time = time.time()
    spar = Spar(server_number, minimum_replicas)
    if percent10_stop is True:
        for i in range(int(len(node_list) / 10)):
            n = node_list[i]
            spar.new_node(n, node_neighbor_dic[n])
            node_num += 1
    else:
        for n in tqdm(node_list):
            spar.new_node(n, node_neighbor_dic[n])
            node_num += 1

    running_time = time.time() - start_time
    master_node_to_server = spar.node_server_dic
    replicas_to_server = spar.replica_server_dic
    ave_replicas_of_nodes = calculate_mean_length(replicas_to_server)
    graph = spar.G
    num_edges = graph.number_of_edges()

    masters_in_each_server = spar.servers_master
    replicas_in_each_server = spar.servers_slave
    ave_master_in_servers = calculate_mean_length(masters_in_each_server)
    ave_slaves_in_servers = calculate_mean_length(replicas_in_each_server)
    averages = [ave_replicas_of_nodes, ave_master_in_servers, ave_slaves_in_servers]
    cost = spar_inter_server_cost(replicas_in_each_server)
    print(file)
    print('node'+str(node_num))
    print('edge'+str(num_edges))
    print('cost'+str(cost))
    print('averages'+str(averages))
    print('data_shape'+str(np.shape(col_data)))
    save_obj(graph, file+'_graph', path)
    save_obj(replicas_in_each_server, file + '_replicas', path)
    save_obj(masters_in_each_server, file + '_masters', path)

    del spar


    return cost, running_time, averages, node_num, num_edges


def spar_experiment_1(percent10_stop=False):
    # Experiment 1 inter server traffic cost



    #digraph_files = ['AmazonSample', 'Amazon', 'Twitter', 'TwitterSample1', 'TwitterSample2', 'Facebook', 'p2pGnutella']
    digraph_files = ['AmazonSample', 'TwitterSample1', 'TwitterSample2', 'Facebook', 'p2pGnutella']
    #digraph_files = ['Amazon', 'Twitter']
    #digraph_files = ['AmazonSample']

    num_server = Constant.SERVER_NUMBER

    # create logger
    # logger_name = "Spar_experiment1"
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create file handler
    log_path = LOG_PATH + '/spar_experiment1.log'
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)

    # create formatter
    fmt = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
    datefmt = "%a %d %b %Y %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt)

    # add handler and formatter to logger
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    save_file_dir = SPAR_GRAPH_SAVE_PATH + '/Fig10_'
    logger.info('Start experiment 1')
    if percent10_stop:
        logger.info('Stop at 10 percent of the data')
    replica_2_result = {}
    minimum_replica = 2
    for file in digraph_files:
        print('Processing 2 replicas' + file)
        cost, running_time, averages, num_nodes, num_edges = test_spar_sample(file, num_server, minimum_replica,
                                                                              percent10_stop, save_file_dir)
        logger.info('file %s, server number = %s, nodes = %s, edges = %s cost = %s, time = %s', file,
                    str(num_server), str(num_nodes), str(num_edges), str(cost), str(running_time))
        logger.info('average: replica_per_node=%s, master_per_server=%s, replicas_per_server=%s',
                    str(averages[0]), str(averages[1]), str(averages[2]))
        replica_2_result[file] = cost

    print(replica_2_result)
    logger.info('replica 2 results: %s', str(replica_2_result))

    save_file_dir = SPAR_GRAPH_SAVE_PATH + '/Fig11_'
    replica_3_result = {}
    minimum_replica = 3
    for file in digraph_files:
        print('Processing 3 replicas' + file)
        cost, running_time, averages, num_nodes, num_edges = test_spar_sample(file, num_server, minimum_replica,
                                                                              percent10_stop, save_file_dir)
        logger.info('file %s, server number = %s, nodes = %s, edges = %s cost = %s, time = %s', file,
                    str(num_server), str(num_nodes), str(num_edges), str(cost), str(running_time))
        logger.info('average: replica_per_node=%s, master_per_server=%s, replicas_per_server=%s',
                    str(averages[0]), str(averages[1]), str(averages[2]))
        replica_3_result[file] = cost

    print(replica_3_result)
    logger.info('replica 3 results: %s', str(replica_3_result))
    logger.info('End experiment 1')


if __name__ == '__main__':
    spar_experiment_1(percent10_stop=True)
