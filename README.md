# CE7490-Group-Porject
CE7490 Fall 2018 Advanced Topics in Distributed System

### Install Guide
We use python 3.6 and Anaconda to manage the environment, the code is running at Ubuntu 16.04 system, and may compatible 
to different systems and versions, but may require some slightly modification to the installation guide we provided following.

#### Install Anaconda and create the conda environment
So firstly, install the [anaconda]() by following the official 
instruction.
Then run the following command at terminal:
```
cd /path/to/CE7490-Group-Project-Python
conda env create -f environment.yml
```

#### Run experiments
Before running any experiments, activate the conda environment first:
```
source activate CE7490-Group-Project-Python
```
For baseline, we implement the Random and SPAR algorithm, which can be running by:
```
python test/random_baseline_test.py
python test/spar_test.py
```
For the offline algorithm, running it by:
```
python test/offline_algo_test.py
```