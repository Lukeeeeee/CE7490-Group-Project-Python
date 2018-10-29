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
    return length/iter


def test_spar_sample(file, server_number, minimum_replicas, percent_stop, path):
    filename = DATASET_PATH + '/' + file + '.txt'
    # path = '././dataset/'
    # filename = path + file + '.txt'

    node_list, node_neighbor_dic, col_data = read_file_to_dict(filename)

    node_num = 0
    start_time = time.time()
    spar = Spar(server_number, minimum_replicas)

    for i in range(int(len(node_list)*percent_stop)):
        n = node_list[i]
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
    save_obj(graph, file+'_graph'+str(percent_stop), path)
    save_obj(replicas_in_each_server, file + '_replicas'+str(percent_stop), path)
    save_obj(masters_in_each_server, file + '_masters'+str(percent_stop), path)

    del spar

    return cost, running_time, averages, node_num, num_edges


def spar_Fig10_11(percent_stop, server_number):
    # Experiment 1 inter server traffic cost
    #digraph_files = ['AmazonSample', 'Amazon', 'Twitter', 'TwitterSample1', 'TwitterSample2', 'Facebook', 'p2pGnutella']
    digraph_files = ['AmazonSample', 'TwitterSample1', 'TwitterSample2', 'Facebook', 'p2pGnutella']
    #digraph_files = ['Amazon', 'Twitter']
    #digraph_files = ['AmazonSample']

    num_server = server_number

    # create logger
    # logger_name = "Spar_experiment1"
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create file handler
    log_path = LOG_PATH + '/spar_Fig10_11_server_'+str(num_server)+'stop_'+str(percent_stop)+'.log'
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
    logger.info('Start experiment Fig.10')
    replica_2_result = {}
    minimum_replica = 2
    for file in digraph_files:
        print('Processing 2 replicas' + file)
        cost, running_time, averages, num_nodes, num_edges,= test_spar_sample(file, num_server, minimum_replica,
                                                                              percent_stop, save_file_dir)
        logger.info('file %s, server number = %s, nodes = %s, edges = %s cost = %s, time = %s', file,
                    str(num_server), str(num_nodes), str(num_edges), str(cost), str(running_time))
        logger.info('average: replica_per_node=%s, master_per_server=%s, replicas_per_server=%s, stop_at =%s',
                    str(averages[0]), str(averages[1]), str(averages[2]), str(percent_stop))
        replica_2_result[file] = cost

    print(replica_2_result)
    logger.info('replica 2 results: %s', str(replica_2_result))
    logger.info('End experiment Fig10')

    logger.info('Start experiment Fig.11')
    save_file_dir = SPAR_GRAPH_SAVE_PATH + '/Fig11_'
    replica_3_result = {}
    minimum_replica = 3
    for file in digraph_files:
        print('Processing 3 replicas' + file)
        cost, running_time, averages, num_nodes, num_edges = test_spar_sample(file, num_server, minimum_replica,
                                                                              percent_stop, save_file_dir)
        logger.info('file %s, server number = %s, nodes = %s, edges = %s cost = %s, time = %s', file,
                    str(num_server), str(num_nodes), str(num_edges), str(cost), str(running_time))
        logger.info('average: replica_per_node=%s, master_per_server=%s, replicas_per_server=%s, stop_at =%s',
                    str(averages[0]), str(averages[1]), str(averages[2]), str(percent_stop))
        replica_3_result[file] = cost

    print(replica_3_result)
    logger.info('replica 3 results: %s', str(replica_3_result))
    logger.info('End experiment Fig11')

def spar_fig3(percent_stop):
    dataset = 'TwitterSample2'
    logging.basicConfig(level=logging.DEBUG,
                        filename=os.path.join(LOG_PATH, '%s_%s_%s_%s' % (
                            time.strftime("%Y-%m-%d_%H-%M-%S"), 'spar_fig3', dataset, str(percent_stop))),
                        filemode='w')
    num_servers = [2,4,8,16,32,64,96,128,256]
    if percent_stop == 0.01:
        num_servers = [2, 4, 6, 8]
    minimum_replica = 0
    logging.info('Experiment Fig.3, different server number, dataset = %s, stop_at = %s', dataset, percent_stop)
    for server_num in num_servers:
        save_file_dir = SPAR_GRAPH_SAVE_PATH + '/Fig3_'+str(server_num)+'_'
        cost, running_time, averages, node_num, num_edges = test_spar_sample(dataset, server_num, minimum_replica,
                                                                             percent_stop, path=save_file_dir)
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


def spar_fig8_9(server_number, fig8=True):
    dataset = 'Facebook'
    if fig8:
        minimum_replicas = 0
        name = 'fig8'
    else:
        minimum_replicas = 3
        name = 'fig9'
    logging.basicConfig(level=logging.DEBUG,
                        filename=os.path.join(LOG_PATH, '%s_%s_%s_%s' % (
                            time.strftime("%Y-%m-%d_%H-%M-%S"), 'spar_'+name, dataset, str(server_number))),
                        filemode='w')

    per_nodes = [0.02, 0.05, 0.08, 0.1, 0.5]
    logging.info('Experiment %s, different node number, dataset = %s, server_num = %s', name, dataset,
                 str(server_number))

    filename = DATASET_PATH + '/' + dataset + '.txt'

    server_number = server_number
    node_list, node_neighbor_dic, col_data = read_file_to_dict(filename)
    num_nodes = []
    for per in per_nodes:
        num_nodes.append(int(per*len(node_list)))
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

    logging.info('End experiment')


def spar_fig15_16(percent_stop=0.1):
    file = 'Facebook'
    server_number = 10
    minimum_replicas = 0

    logging.basicConfig(level=logging.DEBUG,
                        filename=os.path.join(LOG_PATH, '%s_%s_%s_%s' % (
                            time.strftime("%Y-%m-%d_%H-%M-%S"), 'spar_Fig1516', file, str(percent_stop))),
                        filemode='w')

    logging.info('Experiment Fig.1516, dataset = %s, server_num = %s, stop_at = %s', file, str(server_number),
                 str(percent_stop))

    spar = Spar(server_number, minimum_replicas)

    filename = DATASET_PATH + '/' + file + '.txt'

    node_list, node_neighbor_dic, col_data = read_file_to_dict(filename)
    path = SPAR_GRAPH_SAVE_PATH + '/Fig1516' + '_'
    node_num = 0
    start_time = time.time()
    spar = Spar(server_number, minimum_replicas)

    for i in range(int(len(node_list) * percent_stop)):
        n = node_list[i]
        spar.new_node(n, node_neighbor_dic[n])
        node_num += 1

    graph = spar.G
    num_edges = graph.number_of_edges()

    masters_in_each_server = spar.servers_master
    replicas_in_each_server = spar.servers_slave
    replica_list = []
    master_list = []
    for key, data in masters_in_each_server.items():
        master_list.append(len(data))
    for key, data in replicas_in_each_server.items():
        replica_list.append(len(data))
    replica_list = np.array(replica_list)/sum(replica_list)
    master_list = np.array(master_list)/sum(master_list)
    cost = spar_inter_server_cost(replicas_in_each_server)
    logging.info('Fig15:'+str(replica_list))
    logging.info('Fig16:'+str(master_list))

    print(file)
    print('servers' + str(server_number))
    print('node' + str(node_num))
    print('edge' + str(num_edges))
    print('cost' + str(cost))
    save_obj(graph, file + '_graph' + str(percent_stop), path)
    save_obj(replicas_in_each_server, file + '_replicas' + str(percent_stop), path)
    save_obj(masters_in_each_server, file + '_masters' + str(percent_stop), path)

    logging.info('End experiment fig1516')


def spar_fig19(percent_stop = 0.1):
    Phi = [0,1,2,3,4,5,6,7]
    file = 'AmazonSample'
    server_number = 8

    logging.basicConfig(level=logging.DEBUG,
                        filename=os.path.join(LOG_PATH, '%s_%s_%s_%s' % (
                            time.strftime("%Y-%m-%d_%H-%M-%S"), 'spar_Fig19', file, str(percent_stop))),
                        filemode='w')

    logging.info('Experiment Fig.19, dataset = %s, server_num = %s, stop_at = %s', file, str(server_number),
                 str(percent_stop))
    for minimum_replica in Phi:
        save_file_dir = SPAR_GRAPH_SAVE_PATH + '/Fig19_'+str(minimum_replica)+'_'
        cost, running_time, averages, node_num, num_edges = test_spar_sample(file, server_number, minimum_replica,
                                                                             percent_stop, path=save_file_dir)
        logging.info('file %s, server number = %s, nodes = %s, edges = %s cost = %s, time = %s', file,
                    str(server_number), str(node_num), str(num_edges), str(cost), str(running_time))
        logging.info('average: replica_per_node=%s, master_per_server=%s, replicas_per_server=%s',
                    str(averages[0]), str(averages[1]), str(averages[2]))
    logging.info('End experiment fig19')

def spar_experiments():

    print('spar_fig3(0.1)')
    spar_fig3(0.1)
    print('spar_fig3(0.01)')
    spar_fig3(0.5)

    print('spar_fig8(128)')
    spar_fig8_9(128, True)
    print('spar_fig8(64)')
    spar_fig8_9(64, True)
    print('spar_fig9(128)')
    spar_fig8_9(128, False)
    print('spar_fig9(64)')
    spar_fig8_9(64, False)

    print('spar_fig11(0.1,128)')
    spar_Fig10_11(0.5, 128)
    print('spar_fig11(0.1,64)')
    spar_Fig10_11(0.5, 64)
    #spar_fig11(0.01,8)')
    #spar_Fig10_11(0.01, 8)

    print('spar1516')
    spar_fig15_16(percent_stop=0.5)
    #spar_fig15_16(percent_stop=0.01)

    print('spar19')
    spar_fig19(percent_stop=0.1)
    spar_fig19(percent_stop=0.01)


if __name__ == '__main__':
   spar_experiments()


