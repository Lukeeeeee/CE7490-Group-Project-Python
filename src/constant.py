from src.core import Basic


class Constant(Basic):
    PRIMARY_COPY = 1
    NON_PRIMARY_COPY = 2
    VIRTUAL_PRIMARY_COPY = 3

    SSN = 1
    PSSN = 2
    DSN = 3
    PDSN = 3

    # ALGO PARAMETER
    OFFLINE_ETA = 10
    OFFLINE_EPSILON = 10
    LEASET_VIRTUAL_PRIMARY_COPY_NUMBER = 2

    def __init__(self):
        super().__init__()
        self._global_node_id = 0

    @property
    def global_node_id(self):
        return self._global_node_id

    @global_node_id.setter
    def global_node_id(self, val):
        self._global_node_id = val
