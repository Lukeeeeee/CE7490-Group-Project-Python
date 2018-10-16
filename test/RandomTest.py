from src.dataset import Dataset
from src.server.server import Server
from src.randomP.randomP import RandomP
import random


def main():
    network_dataset = Dataset('amazon')
    server_list = [Server(k) for k in range(0, 15)]
    node_list=list(network_dataset.graph.nodes)
    random.shuffle(node_list)
    print('Dataset information:\nNodes Number:',network_dataset.graph.order(),'\nEdge Number:',
          network_dataset.graph.size())
    print('Using Random Partitioning Method...\nServer Number: 16\nVirtual Primary Copy Number: 3'
          '\nWrite Frequency of Nodes: 1')
    m = RandomP(server_list, network_dataset,node_list)
    m.add_new_primary_node()
    m.check_server_load()
    m.check_locality()
    m.compute_inter_sever_cost()


main()






