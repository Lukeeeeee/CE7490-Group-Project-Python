import numpy as np
import networkx as nx
import time
import os
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
        for i in range(int(len(node_list) / 100)):
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
    print('servers'+str(server_number))
    print('node'+str(node_num))
    print('edge'+str(num_edges))
    print('cost'+str(cost))
    print('averages'+str(averages))
    save_obj(graph, file+'_graph', path)
    save_obj(replicas_in_each_server, file + '_replicas', path)
    save_obj(masters_in_each_server, file + '_masters', path)

    del spar


    return cost, running_time, averages, node_num, num_edges


def spar_experiment_1(percent10_stop=False):
    # Experiment 1 inter server traffic cost



    #digraph_files = ['AmazonSample', 'Amazon', 'Twitter', 'TwitterSample1', 'TwitterSample2', 'Facebook', 'p2pGnutella']
    # digraph_files = ['AmazonSample', 'TwitterSample1', 'TwitterSample2', 'Facebook', 'p2pGnutella']
    #digraph_files = ['Amazon', 'Twitter']
    digraph_files = ['AmazonSample']

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

def spar_fig3():
    dataset = 'TwitterSample2'
    logging.basicConfig(level=logging.DEBUG,
                        filename=os.path.join(LOG_PATH, '%s_%s_%s' % (
                            time.strftime("%Y-%m-%d_%H-%M-%S"), 'spar_fig3', dataset)),
                        filemode='w')
    num_servers = [2,4,8,16,32,64,128,256,512,1000]
    minimum_replica = 0
    logging.info('Experiment Fig.3, different server number, dataset = %s', dataset)
    for server_num in num_servers:
        save_file_dir = SPAR_GRAPH_SAVE_PATH + '/Fig3_'+str(server_num)+'_'
        cost, running_time, averages, node_num, num_edges = test_spar_sample(dataset, server_num, minimum_replica,
                                                                             percent10_stop= False, path=save_file_dir)
        logging.info('file %s, server number = %s, nodes = %s, edges = %s cost = %s, time = %s', dataset,
                    str(server_num), str(node_num), str(num_edges), str(cost), str(running_time))
        logging.info('average: replica_per_node=%s, master_per_server=%s, replicas_per_server=%s',
                    str(averages[0]), str(averages[1]), str(averages[2]))
        logging.info('End experiment fig3')


def fig89_check_points(spar, node_num, dataset, server_number, minimum_replicas, path):
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
    print(dataset)
    print('servers' + str(server_number))
    print('node' + str(node_num))
    print('edge' + str(num_edges))
    print('cost' + str(cost))
    print('averages' + str(averages))
    save_obj(graph, dataset + '_graph', path)
    save_obj(replicas_in_each_server, dataset + '_replicas', path)
    save_obj(masters_in_each_server, dataset + '_masters', path)
    return cost, averages, node_num, num_edges


def spar_fig8_9(fig8=True):
    dataset = 'Facebook'
    if fig8:
        minimum_replicas = 0
        name = 'fig8'
    else:
        minimum_replicas = 3
        name = 'fig9'
    logging.basicConfig(level=logging.DEBUG,
                        filename=os.path.join(LOG_PATH, '%s_%s_%s' % (
                            time.strftime("%Y-%m-%d_%H-%M-%S"), 'spar_'+name, dataset)),
                        filemode='w')
    num_nodes = [256,512,1024,2048,4039]
    logging.info('Experiment Fig.3, different server number, dataset = %s', dataset)

    filename = DATASET_PATH + '/' + dataset + '.txt'

    server_number = Constant.SERVER_NUMBER
    node_list, node_neighbor_dic, col_data = read_file_to_dict(filename)

    node_num = 0

    spar = Spar(server_number, minimum_replicas)

    for n in tqdm(node_list):
        spar.new_node(n, node_neighbor_dic[n])
        node_num += 1
        if node_num in num_nodes:
            path = SPAR_GRAPH_SAVE_PATH + '/'+ name+'_' +str(node_num)+'_'
            cost, averages, num, num_edges = fig89_check_points(spar, node_num, dataset, server_number,
                                                                minimum_replicas, path)
            logging.info('file %s, server number = %s, nodes = %s, edges = %s cost = %s', dataset,
                         str(server_number), str(node_num), str(num_edges), str(cost))
            logging.info('average: replica_per_node=%s, master_per_server=%s, replicas_per_server=%s',
                         str(averages[0]), str(averages[1]), str(averages[2]))

    logging.info('End experiment fig3')


if __name__ == '__main__':
    spar_experiment_1(percent10_stop=True)
    # spar_fig3()
    # spar_fig8_9(fig8=True)
