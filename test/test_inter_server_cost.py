from src.algo.inter_server_cost import compute_inter_sever_cost
from src.server.server import Server
import networkx as nx

S1 = Server(1)
S2 = Server(2)

S1.add_node(0, 1, 1)
S1.add_node(1, 1, 1)
S1.add_node(5, 1, 1)
S1.add_node(6, 1, 1)
S1.add_node(2, 2, 1)
S1.add_node(3, 2, 1)
S1.add_node(4, 2, 1)

S2.add_node(2, 1, 1)
S2.add_node(3, 1, 1)
S2.add_node(4, 1, 1)
S2.add_node(1, 2, 1)
S2.add_node(5, 2, 1)
S2.add_node(6, 2, 1)

servers=[S1,S2]

C = compute_inter_sever_cost(servers)
print('Inter server cost of current partitioning is ',C)
