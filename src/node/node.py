from src.core import Basic
import networkx as nx


class Node(Basic):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.server = None
        self.non_primary_copy_server_list = []
        self.virtual_primary_copy_server_list = []
