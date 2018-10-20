from src.algo.offlineAlgo import OfflineAlgo
import networkx as nx
from src.dataset import Dataset
from src.server.server import Server
from src.constant import Constant


def main():
    data = Dataset(dataset_str='facebook')
    data.graph = nx.Graph()
    for i in range(10):
        data.graph.add_node(i)
    for i in range(10):
        data.graph.add_edge(i, (i + 1) % 10)
    server_list = [Server(serer_id=i) for i in range(20)]
    algo = OfflineAlgo(server_list=server_list, network_dataset=data)
    node_list = list(data.graph.nodes)
    node_len = len(node_list)
    for i in range(node_len):
        n = node_list[i]
        print("(%d/%d) Adding node: " % (i, node_len), n)
        algo.add_new_primary_node(node_id=n, write_freq=Constant.WRITE_FREQ)

    algo.node_relocation_process()
    algo.init_merge_process()
    algo.init_group_swap_process()
    algo.virtual_primary_copy_swap()

    print(algo.compute_inter_server_cost())

    for server in server_list:
        print("Server: %d, load: %d" % (server.id, server.get_load()))
        for node in server.graph.nodes:
            print(node, server.graph.nodes[node])


if __name__ == '__main__':
    main()
