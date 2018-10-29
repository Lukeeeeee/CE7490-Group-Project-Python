import networkx as nx
import nxmetis
import pickle
from log.graphs import METIS_GRAPH_SAVE_PATH
from dataset import DATASET_PATH


def read_file_to_list(filename):
    # Read data from non-directed graph like data from txt files
    # Input: filename in string
    # Output:
    # col_data: raw data read as 2-D list, useful for offline cases
    filename = DATASET_PATH + '/' + filename + '.txt'
    col_data = []
    with open(filename) as f:
        data = f.readlines()

    for line in data:
        col_data.append([int(line.strip().split("\t")[0]), int(line.strip().split("\t")[1])])

    return  col_data


def list_to_graph(col, per):
    G = nx.Graph()
    iter = 0
    for e in col:
        G.add_edge(e[0], e[1])
        iter += 1
        if iter > len(col)*per:
            break

    return G


def save_obj(obj, name, path):
    with open(path + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name, path):
    with open(path + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def metis_partitions(graph, num_par, file_name, per):
    par_result = nxmetis.partition(graph, num_par)[1]
    name = '/'+file_name + str(num_par)+'_'+str(per)
    graph_name = '/'+file_name + str(num_par)+'_'+str(per)+'_graph'
    path = METIS_GRAPH_SAVE_PATH
    save_obj(par_result, name, path)
    #save_obj(graph, graph_name, path)

    return graph, par_result

def main(num_par = 128, percent = 0.1):
    digraph_files = ['AmazonSample', 'TwitterSample1', 'TwitterSample2', 'Facebook', 'p2pGnutella']
    for file in digraph_files:
         col = read_file_to_list(file)
         G = list_to_graph(col, percent)
         metis_partitions(G, num_par, file, percent)


'''
def create_replicas(graph, num_par, par_result, minimum_replica):
    G = graph
    master_dict = {}
    slave_dict = {}
    slave_to_server = {}
    node_list = list(G.nodes())


    for i in range(len(par_result)):
        master_dict[i] = par_result[i]
        for node in par_result[i]:
            G.nodes[node]['server'] = i

    for n in node_list:
        slave_dict[n]=[]

    for n in node_list:
        for neighbor in G.neighbors(n):
            server_id = G.nodes[neighbor]['server']
            if server_id != G.nodes[n]['server']:
                slave_dict[server_id].append(neighbor)
                slave_to_server[neighbor] = server_id

    for n in node_list:
        if len(slave_to_server[n]) < minimum_replica:
            diff = minimum_replica - len(slave_to_server[n])
            for i in range(diff):
                ser = minimum_load_server(slave_dict, node_list)
                n


    def minimum_load_server(slave_dict, node_list):
        replica_load_mat = np.zeros_like(node_list)
        for server, replicas_in_server in slave_dict.items():
            replica_load_mat[int(server)] = len(replicas_in_server)

        minimums = np.where(replica_load_mat == replica_load_mat.min())[0]

        if len(minimums) > 1:
            return np.random.choice(minimums)
        else:
            return minimums[0]
'''
if __name__ == '__main__':
    main(128,0.1)
