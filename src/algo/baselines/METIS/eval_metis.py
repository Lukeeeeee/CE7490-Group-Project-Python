import numpy as np
import networkx as nx
import pickle
from graphs.metis import METIS_GRAPH_SAVE_PATH
from dataset import DATASET_PATH
import logging
from log import LOG_PATH
import os
import time


def save_obj(obj, name, path):
    with open(path + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name, path):
    with open(path + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def get_partitions(num_par, file_name, per):
    name = '/'+file_name + str(num_par)+'_'+str(per)
    graph_name = '/'+file_name + str(num_par)+'_'+str(per)+'_graph'
    path = METIS_GRAPH_SAVE_PATH
    par_result = load_obj(name, path)
    graph = load_obj(graph_name, path)
    print(par_result)
    print(np.shape(par_result))
    #print(graph)

    return graph, par_result


def cal_cost(graph, num_par, par_result, minimum_replica):
    G = graph
    master_dict = {}
    slave_dict = {}
    slave_to_server = {}
    node_list = list(G.nodes())
    cost = 0


    for i in range(len(par_result)):
        #master_dict[i] = par_result[i]
        for node in par_result[i]:
            G.nodes[node]['server'] = i

    for n in node_list:
        slave_dict[n]=[]

    for n in node_list:
        inter_edge = 0
        for neighbor in G.neighbors(n):
            server_id = G.nodes[neighbor]['server']
            if server_id != G.nodes[n]['server']:
                inter_edge += 1
        cost += max(inter_edge, minimum_replica)

    return cost


def get_cost():
    minimum_replica = 3
    logging.basicConfig(level=logging.DEBUG,
                        filename=os.path.join(LOG_PATH, '%s_%s' % (
                            time.strftime("%Y-%m-%d_%H-%M-%S"), 'METIS_Fig11')),
                        filemode='w')
    para = [[128,0.5],[128,0.1],[64,0.1],[8,0.01]]
    digraph_files = ['AmazonSample', 'TwitterSample1', 'TwitterSample2', 'Facebook', 'p2pGnutella']
    for num_par, percent in para:
        cost_list = []
        i = 0
        for file in digraph_files:
            print(i)
            G, par = get_partitions(num_par, file, percent)
            cost = cal_cost(G, num_par, par, minimum_replica)
            cost_list.append(cost)
            i+=1

        logging.info('file %s, server number = %s, percent = %s, cost = %s', str(digraph_files),
                        str(num_par), str(percent), str(cost_list))


if __name__ == '__main__':
    get_cost()
