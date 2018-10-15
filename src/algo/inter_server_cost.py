from src.server.server import Server


def compute_inter_sever_cost(servers):          # servers is a list of server
    cost = 0
    for server in servers:
        for node in server.graph:
            if server.graph.nodes[node]['node_type'] == 2:
                cost = cost + server.graph.nodes[node]['write_freq']
    return cost
