import numpy as np
import networkx as nx
import logging
import pickle
from tqdm import tqdm
from src.algo.baselines.SPAR.read_data import read_file_digraph, read_file_ndgraph
from src.algo.baselines.SPAR.Spar import Spar
from dataset import DATASET_PATH
from log import LOG_PATH


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


def test_spar_sample(file, server_number, minimum_replicas, digraph = True):
    filename = DATASET_PATH + file + '.txt'

    if digraph:
        node_list, node_neighbor_dic, col_data = read_file_digraph(filename)
    else:
        node_list, node_neighbor_dic, col_data = read_file_ndgraph(filename)

    spar = Spar(server_number, minimum_replicas)
    for n in tqdm(node_list):
        spar.new_node(n, node_neighbor_dic[n])

    #master_node_to_server = spar.node_server_dic
    #replicas_to_server = spar.replica_server_dic

    masters_in_each_server = spar.servers_master
    replicas_in_each_server = spar.servers_slave


    #graph = spar.G

    return spar_inter_server_cost(replicas_in_each_server)


def spar_experiment_1():
    # Experiment 1 inter server traffic cost
    digraph_files = ['AmazonSample', 'Amazon', 'Twitter', 'TwitterSample1', 'TwitterSample2']
    ndgraph_files = ['Facebook', 'p2pGnutella']
    num_server = 128

    # create logger
    logger_name = "Spar_experiment1"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # create file handler
    log_path = LOG_PATH
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)

    # create formatter
    fmt = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
    datefmt = "%a %d %b %Y %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt)

    # add handler and formatter to logger
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    replica_2_result = {}
    minimum_replica = 2
    for file in digraph_files:
        print('Processing 2 replicas' + file)
        cost = test_spar_sample(file, num_server, minimum_replica, digraph=True)
        logger.info('file %s, server number = %s, minimum replicas = %s, cost = %s', file,
                    str(num_server), str(minimum_replica), str(cost))
        replica_2_result[file] = cost

    for file in ndgraph_files:
        print('Processing 2 replicas' + file)
        cost = test_spar_sample(file, num_server, minimum_replica, digraph=True)
        logger.info('file %s, server number = %s, minimum replicas = %s, cost = %s', file,
                    str(num_server), str(minimum_replica), str(cost))
        replica_2_result[file] = cost

    replica_3_result = {}
    minimum_replica = 3
    for file in digraph_files:
        print('Processing 3 replicas' + file)
        cost = test_spar_sample(file, num_server, minimum_replica, digraph=True)
        logger.info('file %s, server number = %s, minimum replicas = %s, cost = %s', file,
                    str(num_server), str(minimum_replica), str(cost))
        replica_3_result[file] = cost

    for file in ndgraph_files:
        print('Processing 3 replicas' + file)
        cost = test_spar_sample(file, num_server, minimum_replica, digraph=True)
        logger.info('file %s, server number = %s, minimum replicas = %s, cost = %s', file,
                    str(num_server), str(minimum_replica), str(cost))
        replica_3_result[file] = cost


if __name__ == '__main__':
    spar_experiment_1()