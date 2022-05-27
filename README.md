# Python 实现简单区块链

用Python实现区块链并模拟区块链的运行过程

代码参考：

- [用Python从零开始创建区块链](https://learnblockchain.cn/2017/10/27/build_blockchain_by_python#%E7%90%86%E8%A7%A3%E5%B7%A5%E4%BD%9C%E9%87%8F%E8%AF%81%E6%98%8E)
- [Learn Blockchains by Building One](https://hackernoon.com/learn-blockchains-by-building-one-117428612f46)

## 介绍

    区块链是一种分布式数据存储和共享的数据结构。

主要分为以下几个模块：

1. 区块
   1. 构建区块头
   2. 计算交易的Merkle Root
   3. 工作量证明(挖矿)
2. 链
   1. 增加交易到暂存区
   2. 增加区块到区块链
   3. 解决冲突(选取最长的链)
   4. 验证区块链是否有效
3. 账户
   1. 创建账户
   2. 根据账户私钥签名交易
   3. 根据账户公钥验证交易
4. 节点
   1. 创建节点
   2. 注册其他邻居节点
   3. 启动挖矿
   4. 接收交易
   5. 获取邻居节点信息并解决冲突

## 开始

1. 环境

```pip install -r requirements.txt```

2. 启动节点

```python node.py -p 5000```

3. 测试节点各个功能

```python test_node.py```
