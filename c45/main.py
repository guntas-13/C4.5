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