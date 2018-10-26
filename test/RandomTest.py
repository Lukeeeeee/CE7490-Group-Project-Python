from src.dataset import Dataset
from src.server.server import Server
from src.algo.baselines.randomP.randomP import RandomP
from dataset import DATASET_PATH
import random
import time
import os


from src.algo.baselines.SPAR.read_data import read_file_digraph, read_file_ndgraph

def main():

    network_dataset = Dataset('facebook')

    nl, node_neighbor_dic, col_data = read_file_ndgraph(os.path.join(DATASET_PATH, 'Facebook.txt'))

    #10% sampling
    nbunch = nl[0:(len(nl)//10)]
    network_dataset.graph=network_dataset.graph.subgraph(nbunch)

    server_list = [Server(k) for k in range(0, 127)]
    vp_number = 3

    node_list=list(network_dataset.graph.nodes)
    random.shuffle(node_list)
    print('Dataset information:\nNodes Number:',network_dataset.graph.order(),'\nEdge Number:',
          network_dataset.graph.size())
    print('Using Random Partitioning Method...\nServer Number: 128\nVirtual Primary Copy Number:',vp_number,
          '\nWrite Frequency of Nodes: 1')
    start=time.time()
    m = RandomP(server_list, network_dataset,node_list)
    m.add_new_primary_node(server_list,vp_number)
    m.check_server_load()
    m.check_locality()
    end=time.time()
    print('Random Partitioning Time:',end-start,'seconds')
    m.compute_inter_sever_cost()

main()
