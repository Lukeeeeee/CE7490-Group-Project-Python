import numpy as np
import networkx as nx

MAXIMUM_LOAD_DIFFERENCE = 1


class Spar:

    def __init__(self, num_servers, minimum_replicas):
        self.minimum_replicas = minimum_replicas
        self.G = nx.Graph()
        self.nodes = []
        # self.new_node = -1
        # self.new_node_neighbors = []
        # self.node_neighbors = {}

        # Dict server to nodes
        self.servers_master = {}
        self.servers_slave = {}

        self.n_servers = num_servers

        # Dict node master and slave to server
        self.node_server_dic = {}
        self.replica_server_dic = {}

        # Load in servers
        self.load_mat = np.zeros((self.n_servers,))
        self.replica_load_mat = np.zeros((self.n_servers,))

        for i in range(self.n_servers):
            self.servers_master[i] = []
            self.servers_slave[i] = []

    def new_node(self, node, neighbors):
        # self.new_node = node
        # self.new_node_neighbors = neighbors
        self.nodes.append(node)
        self.G.add_node(node)

        # Add edges to graph
        for neighbor in neighbors:
            if neighbor in self.nodes:
                self.G.add_edge(node, neighbor)

        # Assign the node to the server with minimum load
        server_id = self.minimum_load_server()
        self.node_server_dic[node] = server_id
        # print(server_id)
        self.servers_master[server_id].append(node)
        self.replica_server_dic[node] = []

        num_replicas, action = self.swap_create(node, neighbors)

        self.update_master_load()

        # return num_replicas, action

    def swap_create(self, node, neighbors):
        action, target_node, target_server, r_node_server_list, r_neighbor_server_list = self.run_spar(node, neighbors)
        if action == 0:
            for server in r_node_server_list:
                self.servers_slave[server].append(node)
                self.replica_server_dic[node].append(server)

        elif action == 1:
            self.servers_master[self.node_server_dic[node]].remove(node)
            self.node_server_dic[node] = target_server
            self.servers_master[target_server].append(node)
            for server in r_node_server_list:
                self.servers_slave[server].append(node)
                self.replica_server_dic[node].append(server)

        else:
            self.servers_master[self.node_server_dic[target_node]].remove(target_node)
            self.node_server_dic[target_node] = self.node_server_dic[node]
            self.servers_master[self.node_server_dic[node]].append(target_node)
            for server in r_node_server_list:
                self.servers_slave[server].append(node)
                self.replica_server_dic[node].append(server)
            for server in r_neighbor_server_list:
                self.servers_slave[server].append(target_node)
                self.replica_server_dic[node].append(server)
            if len(self.replica_server_dic[target_node]) < self.minimum_replicas:
                num_needed = self.minimum_replicas - len(self.replica_server_dic[target_node])
                self.generate_random_replicas(num_needed, target_node)

        if len(self.replica_server_dic[node]) < self.minimum_replicas:
            num_needed = self.minimum_replicas - len(self.replica_server_dic[node])
            self.generate_random_replicas(num_needed, node)

        return len(r_node_server_list) + len(r_neighbor_server_list), action

    def run_spar(self, node, neighbors):
        # Heuristic algorithem to try three actions among all neighbors
        optimal_action = 0
        target_node = None
        target_server = None
        num_replicas, server_to_create_replicas = self.stay(node, neighbors)
        current_least_replicas = num_replicas
        optimal_server_to_create_node_replicas = server_to_create_replicas
        optimal_server_to_create_neighbor_replicas = []

        for neighbor in neighbors:
            if neighbor in self.nodes:
                num_replicas, server_to_create_replicas = self.swap_to_other(node, neighbor, neighbors)
                if num_replicas < current_least_replicas:
                    if len(self.node_server_dic[neighbor]) - len(self.node_server_dic[node]) <= MAXIMUM_LOAD_DIFFERENCE:
                        optimal_action = 1
                        target_server = self.node_server_dic[neighbor]
                        optimal_server_to_create_node_replicas = server_to_create_replicas

                num_replicas, server_to_create_node_replicas, server_to_create_neighbor_replicas = self.swap_from_other(
                    node, neighbor, neighbors)
                if num_replicas < current_least_replicas:
                    if len(self.node_server_dic[node]) - len(self.node_server_dic[neighbor]) <= MAXIMUM_LOAD_DIFFERENCE:
                        optimal_action = 2
                        target_server = self.node_server_dic[neighbor]
                        target_node = neighbor
                        optimal_server_to_create_replicas = server_to_create_node_replicas
                        optimal_server_to_create_neighbor_replicas = server_to_create_neighbor_replicas

        return optimal_action, target_node, target_server, optimal_server_to_create_node_replicas, optimal_server_to_create_neighbor_replicas

    def stay(self, node, neighbors):
        # Get the number of replicas that need to be create if node stays
        # only replicas of the new node need to be created
        server_list = []
        for neighbor in neighbors:
            if neighbor in self.nodes:
                if self.node_server_dic[neighbor] not in server_list:
                    if self.node_server_dic[neighbor] != self.node_server_dic[node]:
                        server_list.append(self.node_server_dic[neighbor])
        return len(server_list), server_list

    def swap_to_other(self, node, node_neighbor, neighbors):
        # Get the number of replicas that need to be create if node swap to node_neighbor's server
        # only replicas of the new node need to be created
        server_list = [self.node_server_dic[node]]
        for neighbor in neighbors:
            if neighbor in self.nodes:
                if self.node_server_dic[neighbor] not in server_list:
                    if self.node_server_dic[neighbor] != self.node_server_dic[node_neighbor]:
                        server_list.append(self.node_server_dic[neighbor])
        return len(server_list), server_list

    def swap_from_other(self, node, node_neighbor, neighbors):
        # Get the number of replicas that need to be create if neighbor swap to node's server
        # both neighbor and this node need to create replicas
        server_neighbor_replicas = [self.node_server_dic[node_neighbor]]
        server_node_replicas = []
        for neighbor_neighbor in self.G.neighbors(node_neighbor):
            if neighbor_neighbor in self.nodes:
                if self.node_server_dic[neighbor_neighbor] not in server_neighbor_replicas:
                    if self.node_server_dic[neighbor_neighbor] != self.node_server_dic[node]:
                        if neighbor_neighbor not in self.servers_slave[self.node_server_dic[neighbor_neighbor]]:
                            server_neighbor_replicas.append(self.node_server_dic[neighbor_neighbor])

        for neighbor in neighbors:
            if neighbor in self.nodes:
                if self.node_server_dic[neighbor] not in server_node_replicas:
                    if self.node_server_dic[neighbor] != self.node_server_dic[node]:
                        server_node_replicas.append(self.node_server_dic[neighbor])

        return len(server_node_replicas) + len(server_neighbor_replicas), server_node_replicas, server_neighbor_replicas

    def update_master_load(self):
        for server, nodes_in_server in self.servers_master.items():
            self.load_mat[int(server)] = len(nodes_in_server)

        for server, replicas_in_server in self.servers_slave.items():
            self.replica_load_mat[int(server)] = len(replicas_in_server)

    def minimum_load_server(self, master=True):
        if master:
            minimums = np.where(self.load_mat == self.load_mat.min())[0]
        else:
            minimums = np.where(self.replica_load_mat == self.replica_load_mat.min())[0]

        if len(minimums) > 1:
            return np.random.choice(minimums)
        else:
            return minimums[0]

    def generate_random_replicas(self, number, node):
        for i in range(number):
            rand_server = self.minimum_load_server(master=False)
            self.servers_slave[rand_server].append(node)
            self.replica_server_dic[node].append(rand_server)
