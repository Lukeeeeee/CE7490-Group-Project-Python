from src.server.server import Server
from src.constant import Constant


def compute_inter_sever_cost(servers):          # servers is a list of server
    cost = 0
    for server in servers:
        for node in server.graph:
            if server.graph.nodes[node]['node_type'] == Constant.NON_PRIMARY_COPY or server.graph.nodes[node][
                'node_type'] == Constant.VIRTUAL_PRIMARY_COPY:
                cost = cost + server.graph.nodes[node]['write_freq']
    return cost


def compute_inter_sever_cost_graph(graphs):  # servers is a list of server
    cost = 0
    for graph in graphs:
        for node in graph:
            if graph.nodes[node]['node_type'] == Constant.NON_PRIMARY_COPY or graph.nodes[node][
                'node_type'] == Constant.VIRTUAL_PRIMARY_COPY:
                cost = cost + graph.nodes[node]['write_freq']
    return cost
