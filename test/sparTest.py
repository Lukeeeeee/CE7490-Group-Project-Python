from src.algo.baselines.SPAR.spar_sample import test_spar_sample
from dataset import DATASET_PATH
import os

if __name__ == '__main__':
    test_spar_sample(dataset_file=os.path.join(DATASET_PATH, 'AmazonSample.txt'))
