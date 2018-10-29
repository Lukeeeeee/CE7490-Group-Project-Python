import os
import sys

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(CURRENT_PATH)
PAR_PATH = os.path.abspath(os.path.join(CURRENT_PATH, os.pardir))
sys.path.append(PAR_PATH)
from src.algo.baselines.SPAR.spar_sample import spar_fig3, spar_fig8_9, spar_inter_server_cost, test_spar_sample
from dataset import DATASET_PATH
import os

if __name__ == '__main__':
    # Baseline Algorithm SPAR
    # Run experiments that corresponding to figure 3 in original paper
    spar_fig3()
    # Run experiments that corresponding to figure 8 in original paper
    spar_fig8_9(fig8=True)
