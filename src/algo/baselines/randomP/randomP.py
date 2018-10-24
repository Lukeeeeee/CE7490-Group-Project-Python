from src.core import Basic
import random


class RandomP(Basic):
    def __init__(self, server_list, network_dataset, node_list):
        super().__init__()
        self.server_list = server_list
        self.network_dataset = network_dataset
        self.node_list = node_list

    def add_new_primary_node(self,server_list,vp_number):
        i = 0
        q = len(server_list)//(vp_number+1)
        if vp_number == 3:
            a = q
            b = q * 2
            c = q * 3
            for n in self.node_list:
                if i > len(self.server_list) - 1:
                    i = 0
                if a > len(self.server_list) - 1:
                    a = 0
                if b > len(self.server_list) - 1:
                    b = 0
                if c > len(self.server_list) - 1:
                    c = 0
                primary_server = self.server_list[i]
                self.add_primary_copy_to_server(node_id=n, server=primary_server)

                vps1 = self.server_list[a]
                vps2 = self.server_list[b]
                vps3 = self.server_list[c]
                self.add_virtual_primary_copy_to_server(node_id=n, server=vps1)
                self.add_virtual_primary_copy_to_server(node_id=n, server=vps2)
                self.add_virtual_primary_copy_to_server(node_id=n, server=vps3)

                i = i + 1
                a = a + 1
                b = b + 1
                c = c + 1
        elif vp_number == 2:
            a = q
            b = q * 2
            for n in self.node_list:
                if i > len(self.server_list) - 1:
                    i = 0
                if a > len(self.server_list) - 1:
                    a = 0
                if b > len(self.server_list) - 1:
                    b = 0
                primary_server = self.server_list[i]
                self.add_primary_copy_to_server(node_id=n, server=primary_server)

                vps1 = self.server_list[a]
                vps2 = self.server_list[b]

                self.add_virtual_primary_copy_to_server(node_id=n, server=vps1)
                self.add_virtual_primary_copy_to_server(node_id=n, server=vps2)

                i = i + 1
                a = a + 1
                b = b + 1
        else:
            print('vp_number should be 2 or 3')


    def add_primary_copy_to_server(self, node_id,  server):
        server.add_node(node_id=node_id, node_type=1, write_freq=1)

    def add_virtual_primary_copy_to_server(self,node_id, server):
        server.add_node(node_id=node_id, node_type=3, write_freq=1)

    def add_non_primary_copy_to_server(self,node_id, server):
        server.add_node(node_id=node_id, node_type=2, write_freq=1)

    def check_locality(self):
        for server in self.server_list:
            rp=[]
            for node in server.graph:
                if server.graph.nodes[node]['node_type'] == 1:
                    for n in self.network_dataset.graph.neighbors(node):
                        if not server.graph.has_node(n):
                            rp.append(n)
            for i in rp:
                if not server.graph.has_node(i):
                    self.add_non_primary_copy_to_server(node_id=i, server=server)

    def compute_inter_sever_cost(self):
        cost = 0
        for server in self.server_list:
            for node in server.graph:
                if server.graph.nodes[node]['node_type'] == 2:
                    cost = cost + server.graph.nodes[node]['write_freq']
        print('Inter-Server Cost: ',cost,)

    def check_server_load(self):
        server_load_list=[]
        for server in self.server_list:
            server_load_list.append(len(server.graph))
        if max(server_load_list)-min(server_load_list)<=1:
            print('Load of servers are balanced.')

    def find_primary_server(self,node_id):
        for server in self.server_list:
            if server.graph.has_node(node_id):
                if server.graph.nodes[node_id]['node_type']==1:
                    print('The primary copy of Node',node_id,'is assigned on server',server.id)
