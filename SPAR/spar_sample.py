import numpy as np
import networkx as nx
from tqdm import tqdm
from src.read_data import read_file_digraph, read_file_ndgraph
from src.Spar import Spar

if __name__ == '__main__':

    filename = 'AmazonSample.txt'

    node_list, node_neighbor_dic, col_data = read_file_digraph(filename)

    spar = Spar(128)
    for n in tqdm(node_list):
        spar.new_node(n, node_neighbor_dic[n])

    master_node_to_server = spar.node_server_dic
    replicas_to_server = spar.replica_server_dic

    masters_in_each_server = spar.servers_master
    replicas_in_each_server = spar.servers_slave

    graph = spar.G

    print(masters_in_each_server)
