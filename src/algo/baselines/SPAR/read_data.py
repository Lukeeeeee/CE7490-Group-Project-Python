
def read_file_digraph(filename):
    # Read data from directed graph like data from txt files
    # Input: filename in string
    # Output:
    # node_list: list that contains distinct node ids
    # node_neighbor_dic: a dictionary that contains neighbors for each node
    # col_data: raw data read as 2-D list, useful for offline cases

    col_data = []
    with open(filename) as f:
        data = f.readlines()

    for line in data:
        col_data.append([int(line.strip().split("\t")[0]) ,int(line.strip().split("\t")[1])])

    node_list = []
    node_neighbor_dic = {}
    node_list.append(col_data[0][0])
    node_neighbor_dic[col_data[0][0]] = []
    node_neighbor_dic[col_data[0][0]].append(col_data[0][1])
    for i in range(1 ,len(col_data)):
        if col_data[ i -1][0] == col_data[i][0]:
            node_neighbor_dic[col_data[i][0]].append(col_data[i][1])
        else:
            node_list.append(col_data[i][0])
            node_neighbor_dic[col_data[i][0]] = []
            node_neighbor_dic[col_data[i][0]].append(col_data[i][1])

    return node_list, node_neighbor_dic, col_data


def read_file_ndgraph(filename):
    # Read data from non-directed graph like data from txt files
    # Input: filename in string
    # Output:
    # node_list: list that contains distinct node ids
    # node_neighbor_dic: a dictionary that contains neighbors for each node
    # col_data: raw data read as 2-D list, useful for offline cases

    col_data = []
    with open(filename) as f:
        data = f.readlines()

    for line in data:
        col_data.append([int(line.strip().split("\t")[0]), int(line.strip().split("\t")[1])])

    node_list = []
    node_neighbor_dic = {}

    for i in range(len(col_data)):
        for j in range(2):
            _j = 1 ^ j
            if col_data[i][j] not in node_list:
                node_list.append(col_data[i][j])
                node_neighbor_dic[col_data[i][j]] = {}
                node_neighbor_dic[col_data[i][j]] = []

            node_neighbor_dic[col_data[i][j]].append(col_data[i][_j])

    return node_list, node_neighbor_dic, col_data
