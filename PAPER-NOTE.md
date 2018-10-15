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
