from src.server.server import Server
from src.constant import Constant


def compute_inter_sever_cost(servers):          # servers is a list of server
    cost = 0
    for server in servers:
        for node in server.graph:
            if server.graph.nodes[node]['node_type'] == Constant.NON_PRIMARY_COPY:
                cost = cost + server.graph.nodes[node]['write_freq']
    return cost
