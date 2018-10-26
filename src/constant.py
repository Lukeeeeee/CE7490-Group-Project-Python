from src.core import Basic
import logging


class Constant(Basic):
    PRIMARY_COPY = 1
    NON_PRIMARY_COPY = 2
    VIRTUAL_PRIMARY_COPY = 3

    SSN = 1
    PSSN = 2
    DSN = 3
    PDSN = 4

    # node
    WRITE_FREQ = 10.0

    # ALGO PARAMETER
    MAX_LOAD_DIFFERENCE_AMONG_SERVER = 1
    LEAST_VIRTUAL_PRIMARY_COPY_NUMBER = 3
    MAX_RELOCATE_ITERATION = 1
    SERVER_NUMBER = 10

    # Merge
    MERGED_GROUP_LOOSE_CONSTRAINT_EPSILON = 4

    def __init__(self):
        super().__init__()
        self._global_node_id = 0
        self.log_out()

    @property
    def global_node_id(self):
        return self._global_node_id

    @global_node_id.setter
    def global_node_id(self, val):
        self._global_node_id = val

    def log_out(self):
        logging.info("MERGED_GROUP_LOOSE_CONSTRAINT_EPSILON %d" % self.MERGED_GROUP_LOOSE_CONSTRAINT_EPSILON)
        logging.info("SERVER_NUMBER %d" % self.SERVER_NUMBER)
        logging.info("MAX_RELOCATE_ITERATION %d" % self.MAX_RELOCATE_ITERATION)
        logging.info("LEAST_VIRTUAL_PRIMARY_COPY_NUMBER %d" % self.LEAST_VIRTUAL_PRIMARY_COPY_NUMBER)
        logging.info("MAX_LOAD_DIFFERENCE_AMONG_SERVER %d" % self.MAX_LOAD_DIFFERENCE_AMONG_SERVER)
