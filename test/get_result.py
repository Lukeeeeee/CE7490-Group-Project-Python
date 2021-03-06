from log import LOG_PATH
import glob
import os
import json


def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def export_json(file_path, dict):
    if not os.path.exists(os.path.dirname(file_path)):
        os.mkdir(path=os.path.dirname(file_path))
    with open(file_path, 'w') as f:
        json.dump(dict, f, indent=4, sort_keys=True)


def find_path_list(path, key_word, ex_word):
    path = [os.path.join(path, o) for o in os.listdir(path) if os.path.isdir(os.path.join(path, o))]
    res = []
    for path_i in path:
        flag = True
        for key in key_word:
            if key not in path_i:
                flag = False
        for key in ex_word:
            if key in path_i:
                flag = False
        if flag is True:
            res.append(path_i)
    return res


def get_res(path_list):
    for path in path_list:
        if os.path.isfile(os.path.join(path, 'log')):
            with open(os.path.join(path, 'log'), 'r') as f:
                last_two_line = f.readlines()[-2:]
                last_line = last_two_line[1] if last_two_line[1] != '\n' else last_two_line[0]
                cost = float(last_line.split(' ')[-1])
                print(path, cost)


def get_update_res(path_list):
    from src.algo.operation import Operation
    for path in path_list:
        if os.path.isfile(os.path.join(path, 'log')):
            with open(os.path.join(path, 'log'), 'r') as f:
                last_two_line = f.readlines()[-2:]
                last_line = last_two_line[1] if last_two_line[1] != '\n' else last_two_line[0]
                cost = float(last_line.split(' ')[-1])
                print(path, cost)
                if os.path.isfile(path + '/dataset_graph.gpickle'):
                    g, server_g = Operation.load_log(log_path=path)
                    print("update cost is %f" % Operation.remove_redundant_node_on_graph(g, server_g))


if __name__ == '__main__':
    # this script is used to get the result from the log directory by finding the path that contains specific key words
    key_word = ['fig_19', '0.1']
    get_update_res(path_list=find_path_list(path=LOG_PATH + '/',
                                            key_word=key_word,
                                            ex_word=[]))
