from src.dataset import Dataset
from src.server.server import Server
from src.algo.baselines.randomP.randomP import RandomP
from dataset import DATASET_PATH
import random
import time
import os
from src.dataset import read_file_to_dict
from graphs.random import RANDOM_GRAPH_PATH


def main():

    network_dataset = Dataset('twitters2')

    nl = read_file_to_dict(os.path.join(DATASET_PATH, 'TwitterSample2.txt'))

    #10% sampling
    nbunch = nl[0:int(len(nl)//2)]
    network_dataset.graph=network_dataset.graph.subgraph(nbunch)

    server_list = [Server(k) for k in range(0, 512)]
    vp_number = 0

    node_list=list(network_dataset.graph.nodes)
    random.shuffle(node_list)
    print('Dataset information: TwitterSample2\nNodes Number:',network_dataset.graph.order(),'\nEdge Number:',
          network_dataset.graph.size())
    print('Using Random Partitioning Method...\nServer Number:',len(server_list),'\nVirtual Primary Copy Number:',vp_number,
          '\nWrite Frequency of Nodes: 1')
    start=time.time()
    m = RandomP(server_list, network_dataset,node_list)
    m.add_new_primary_node(server_list,vp_number)
    m.check_server_load()
    m.check_locality()
    end=time.time()
    print('Random Partitioning Time:',end-start,'seconds')
    m.compute_inter_sever_cost()
    path = RANDOM_GRAPH_PATH
    m.save_all(path)


main()
