#!/usr/bin/env python
from c45 import C45

c1 = C45("../data/iris/iris.data", "../data/iris/iris.names")
c1.fetchData()
c1.preprocessData()
c1.generateTree()
c1.visualize("iris", "../trees")
c1.printTree()

print("="*100)

c2 = C45("../data/golf/weather.data", "../data/golf/weather.names")
c2.fetchData()
c2.preprocessData()
c2.generateTree()
c2.visualize("golf", "../trees")
c2.printTree()

print("="*100)

c3 = C45("../data/sepsis/CRP.data", "../data/sepsis/CRP.names")
c3.fetchData()
c3.preprocessData()
c3.generateTree()
c3.visualize("sepsis", "../trees")
c3.printTree()

print("="*100)

c4 = C45("../data/sepsis/CRP.data", "../data/sepsis/CRP.names", maxDepth = 5)
c4.fetchData()
c4.preprocessData()
c4.generateTree()
c4.visualize("sepsisDepth5", "../trees")
c4.printTree()