JPR: Exploring Joint Partitioning and Replication for Traffic Minimization in Online Social Networks

1. 做network的partitioning and replication 算法。
2. 数据集是从Facebook爬虫爬下来的。
3. 没有公布源码。
4. 论文里实验结果和另外5中算法进行了对比。


Scalable Minimum-Cost Balanced Partitioning of Large-Scale Social Networks: Online and Offline Solutions

1. 做network的partitioning算法
2. 提出了online offline两个版本的算法
3. baseline比较了SPRA, Random两个结果，部分实验还比较了METIS 算法
4. 在不同的几个数据集上都跑了实验。（代码实现好后，在SNAP上跑应该很容易）
5. 无源码


Optimizing Cost for Online Social Networks on Geo-Distributed Clouds

1. 提出了一个data replacement算法，实现的是类似partitioning and replication功能。
2. 和greedy random SPAR, METIS 在不同参数设置下进行了比较
3. 无源码


Multi-Objective Data Placement for Multi-Cloud Socially Aware Services

1.以距离、价格、碳排放为目标的数据存放优化问题
2.用1-8个slave replicas作为对比实验
3.作者自己收集（爬或者接口？）推特数据并做预处理使用，未提供下载途径
4.作者用C++，用gco-v3 graph cut库编写
5.无开源代码


Adaptive Influence Maximization in Dynamic Social Networks

1.Influence Maximization problem, choosing minimum seeds，提出A-greedy算法
2.比较了 greedy  A-greedy  H-greedy和random
3.数据集使用了HEP和Wiki，都在SNAP中
4.无开源代码


Least Cost Influence Maximization Across Multiple Social Networks

1.LCI problem, 提出了一种lossless couple network frame
2.实验对比了coupled nets和单独网络的实验效果
3.使用了多个数据集，进行了多种数据集组合实验
4.无开源代码


```
1. clone this repo
2. unzip src/Snap-4.1.zip into src/Snap-4.1
3, cd  src/Snap-4.1 
4. run: make all
3. Build Tareget Test in Clion to check if it runs ok
```

### Exp detail

Must run
```
1. Fig3 on twitter sample 2
    1.1 10% data, server count 2, 4, 8, 16, 32, 64, 96, 128
    1.2 1% data, server count 2, 4, 6, 8
    # 1.3 50% data server count  2, 4, 8, 16, 32, 64, 96, 128, 256, 512
      
2. Fig8 on facebook 
    2.1 %2, %5, %8, 10% 50% data, server count 128
    2.2 %2, %5, %8, 10% 50% data, server count 64
   
3. Fig9 on facebook 
    3.1 %2, %5, %8, 10% 50% data, server count 128
    3.2 %2, %5, %8, 10% 50% data, server count 64

4. Fig11 all dataset
    4.1 10% data, server count 128
    4.2 10% data, server count 64
    4.3 1% data, server count 8
    4.4 50% data, server count 128****

5. Fig 15 facebook
    5.1 10% data
    5.2 1% data
    5.3 50% data

5. Fig 16 facebook
    5.1 10% data
    5.2 1% data
    5.3 50% data

6.Fig 19 Amazon sample 
    6.1 10% data
    6.2 1% data
```

Optional run
```
Fig 4 twitter sample 2, 10%
Fig 12 all dataset 10%
Fig 13 
Fig 14
```



### Due: 29 Oct.

Proposed Plan:

`Week 1 9.24-9.30`

Build a basic framework of codes by Dong, Li and Wei will review C++ syntax.

`Week 2 and Week 3 10.1-10.14`

Distribute the code assignments to each one considering the different experiments. Then retrive the results and visulize the results.

`Week 4 10.14-10.21`

Write the report.

`Week 5 10.22-10.29`

Extra time to use in case of delay.


### Experiment List
1. Inter Server Traffic Cost (Fig 10, 11)
```
1.1 under different datasets (Facebook, rxiv, Twitter etc.) 
1.2 with Random, SPAR, Online and Offline
1.3 Various parameters: (Server number K = 128, Virtual primary copies Ψ = 3) (Server number K = 128, Virtual primary copies Ψ = 2)
    
```
    
2. Inter Server Traffic Cost (Fig 8, 9)
```
2.1 Different node number  
2.2 SPAR, Online, Offline
```

    
3. Inter Server Traffic Cost (Fig 3)
```
3.1 Different numbers of servers K
3.2 with Dataset Twitter Sample 2
3.3 Random, SPAR, Online, Offline
```

4, Execution Time (Fig 4)
```
4.1 Different numbers of servers K
4.2 with Dataset Twitter Sample 2
4.3 Random, SPAR, Online
```

5. Execution Time (Fig 12)
```
5.1 Different datasets 
5.2 SPAR, Online
5.3 K = 128 Ψ=3
```
    
6. Inter Server Traffic Cost with traffic weight (Fig 13)
```
6.1 Amazon Twitter
6.2 Random, SPAR, Online, Offline
6.3 K = 128 Ψ=0
```

7. Execution Time with traffic weight (Fig 14)
```
7.1 Twitter Amazon
7.2 SPAR, Online
7.3 K = 128 Ψ=0

```

8. Replica and Nodal Distribution (Fig 15, 16)
```
8.1 Facebook 
8.2 K = 10 Ψ=0
```   

9. Inter Server Traffic Cost with increasing number of virtual primary copies
```
    9.1 Random, SPAR, Online, Offline
    9.2 Arxiv, K=8
    9.3 Various Ψ=0..7
```    

10. Replication reduction and nodes moved per event
```
10.1 Facebook
10.2 16 server, epsilon = 1
```


### Code Requirements
#### Data structure
#### For node:
```
1. We need append more attributes to a node:
primary copy, virtual primary copy and non-primary copy.

Each node no matter its type, will have a unique ID

2. For a primary copy, we need to record all his virtual primary copy and non-primary copy's id

3. Node different relation: 4 types SSN PSSN DSN PDSN, also compute the gain and bonus

```

#### For edge:
```
1. Edge will be classfied into inter-server and intra server edge
```
#### For graph:

```
1. Construct a server as a directed graph
2. Server should have load info
3. For original network structure, we should have a graph
4. for ssn pssn dns pdsn, compute its value in each server

```


### Metric and Algorithm
#### Metric
```
1. cost = storage cost and inter-server traffic costs
2. server change benefit SCB

```

#### Off line Algo
```
1. node add, del 
2. edge add, del
3. node swap among server
```

offline algo flow
```
1. initial assignment
2. data availability: meet the constraint on basic network 
3. node relication and swapping  
4. group based merging and swapping

```

online algo flow
```
1. initial assignment 
2. node relication and swapping 
3. merging and group-based swapping 
to be done!
```
