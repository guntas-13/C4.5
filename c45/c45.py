import math
from graphviz import Digraph
class C45:

	"""Creates a decision tree with C4.5 algorithm"""
	def __init__(self, pathToData,pathToNames, maxDepth=None):
		self.filePathToData = pathToData
		self.filePathToNames = pathToNames
		self.data = []
		self.classes = []
		self.numAttributes = -1 
		self.attrValues = {}
		self.attributes = []
		self.tree = None
		self.maxDepth = maxDepth

	def fetchData(self):
		with open(self.filePathToNames, "r") as file:
			classes = file.readline()
			self.classes = [x.strip() for x in classes.split(",")]
			#add attributes
			for line in file:
				[attribute, values] = [x.strip() for x in line.split(":")]
				values = [x.strip() for x in values.split(",")]
				self.attrValues[attribute] = values
		self.numAttributes = len(self.attrValues.keys())
		self.attributes = list(self.attrValues.keys())
		with open(self.filePathToData, "r") as file:
			for line in file:
				row = [x.strip() for x in line.split(",")]
				if row != [] or row != [""]:
					self.data.append(row)

	def preprocessData(self):
		for index,row in enumerate(self.data):
			for attr_index in range(self.numAttributes):
				if(not self.isAttrDiscrete(self.attributes[attr_index])):
					self.data[index][attr_index] = float(self.data[index][attr_index])

	def printTree(self):
		self.printNode(self.tree)
	
	def add_nodes(self, dot, node, parent_id=None, edge_label=None):
		node_id = str(id(node))
		
		if node.isLeaf:
			label = f"Class = {node.label}"
			# Leaf nodes with rounded rectangle shape
			dot.node(node_id, label, 
					shape='box', 
					style='filled', 
					fillcolor='#E8F5E8', 
					# fontcolor='#2E7D2E',
					color='#4CAF50')
		else:
			if node.threshold is None:
				label = f"{node.label}\n(discrete)"
			else:
				label = f"{node.label}\n<= {node.threshold:.2f}?"
			# Decision nodes with diamond shape and better spacing
			dot.node(node_id, label, 
					shape='diamond', 
					style='filled', 
					fillcolor='#E3F2FD', 
					# fontcolor='#1565C0',
					color='#2196F3',
					width='2.0',
					height='0.8')
		
		if parent_id:
			# Edges with softer colors and better spacing
			dot.edge(parent_id, node_id, 
					label=edge_label or "")
		
		# Recurse to children
		if not node.isLeaf:
			if node.threshold is not None:
				# Numeric split: two children (<=, >)
				self.add_nodes(dot, node.children[0], node_id, f"<= {node.threshold:.2f}")
				self.add_nodes(dot, node.children[1], node_id, f"> {node.threshold:.2f}")
			else:
				# Discrete split: label edges with attribute values
				for idx, child in enumerate(node.children):
					# Get value label from attrValues stored in tree
					val = self.attrValues[node.label][idx]
					self.add_nodes(dot, child, node_id, str(val))
     
	def visualize(self, fileName, directory):
		dot = Digraph()
		dot.attr(rankdir='TB')
		dot.attr('graph', bgcolor='white', fontsize='15', nodesep='0.85')
		dot.attr('node', fontsize='15')
		dot.attr('edge', fontsize='15')
		
		self.add_nodes(dot, self.tree)
		dot.render(fileName, directory, format="svg", cleanup=True)

	def printNode(self, node, indent=""):
		if not node.isLeaf:
			if node.threshold is None:
				#discrete
				for index,child in enumerate(node.children):
					if child.isLeaf:
						print(indent + node.label + " = " + self.attrValues[node.label][index] + " : " + child.label)
					else:
						print(indent + node.label + " = " + self.attrValues[node.label][index] + " : ")
						self.printNode(child, indent + "	")
			else:
				#numerical
				leftChild = node.children[0]
				rightChild = node.children[1]
				if leftChild.isLeaf:
					print(indent + node.label + " <= " + str(node.threshold) + " : " + leftChild.label)
				else:
					print(indent + node.label + " <= " + str(node.threshold)+" : ")
					self.printNode(leftChild, indent + "	")

				if rightChild.isLeaf:
					print(indent + node.label + " > " + str(node.threshold) + " : " + rightChild.label)
				else:
					print(indent + node.label + " > " + str(node.threshold) + " : ")
					self.printNode(rightChild , indent + "	")

	def generateTree(self):
		self.tree = self.recursiveGenerateTree(self.data, self.attributes, depth=0)

	def recursiveGenerateTree(self, curData, curAttributes, depth=0):
		allSame = self.allSameClass(curData)
		
		if self.maxDepth is not None and depth >= self.maxDepth:
			# Reached max depth, return a leaf with majority class
			return Node(True, self.getMajClass(curData), None)

		if len(curData) == 0:
			#Fail
			return Node(True, "Fail", None)
		elif allSame is not False:
			#return a node with that class
			return Node(True, allSame, None)
		elif len(curAttributes) == 0:
			#return a node with the majority class
			majClass = self.getMajClass(curData)
			return Node(True, majClass, None)
		else:
			(best,best_threshold,splitted) = self.splitAttribute(curData, curAttributes)
			remainingAttributes = curAttributes[:]
			remainingAttributes.remove(best)
			node = Node(False, best, best_threshold)
			node.children = [self.recursiveGenerateTree(subset, remainingAttributes, depth + 1)
                    if subset else Node(True, self.getMajClass(curData), None)
    				for subset in splitted
                    ]
			return node

	def getMajClass(self, curData):
		freq = [0]*len(self.classes)
		for row in curData:
			index = self.classes.index(row[-1])
			freq[index] += 1
		maxInd = freq.index(max(freq))
		return self.classes[maxInd]

	def allSameClass(self, data):
		for row in data:
			if row[-1] != data[0][-1]:
				return False
		return data[0][-1]

	def isAttrDiscrete(self, attribute):
		if attribute not in self.attributes:
			raise ValueError("Attribute not listed")
		elif len(self.attrValues[attribute]) == 1 and self.attrValues[attribute][0] == "continuous":
			return False
		else:
			return True

	def splitAttribute(self, curData, curAttributes):
		splitted = []
		maxEnt = -1*float("inf")
		best_attribute = -1
		#None for discrete attributes, threshold value for continuous attributes
		best_threshold = None
		for attribute in curAttributes:
			indexOfAttribute = self.attributes.index(attribute)
			if self.isAttrDiscrete(attribute):
				#split curData into n-subsets, where n is the number of 
				#different values of attribute i. Choose the attribute with
				#the max gain
				valuesForAttribute = self.attrValues[attribute]
				subsets = [[] for a in valuesForAttribute]
				for row in curData:
					for index in range(len(valuesForAttribute)):
						if row[indexOfAttribute] == valuesForAttribute[index]:
							subsets[index].append(row)
							break
				e = self.gain(curData, subsets)
				if e > maxEnt:
					maxEnt = e
					splitted = subsets
					best_attribute = attribute
					best_threshold = None
			else:
				#sort the data according to the column.Then try all 
				#possible adjacent pairs. Choose the one that 
				#yields maximum gain
				curData.sort(key = lambda x: x[indexOfAttribute])
				for j in range(0, len(curData) - 1):
					if curData[j][indexOfAttribute] != curData[j+1][indexOfAttribute]:
						threshold = (curData[j][indexOfAttribute] + curData[j+1][indexOfAttribute]) / 2
						less = []
						greater = []
						for row in curData:
							if(row[indexOfAttribute] > threshold):
								greater.append(row)
							else:
								less.append(row)
						e = self.gain(curData, [less, greater])
						if e >= maxEnt:
							splitted = [less, greater]
							maxEnt = e
							best_attribute = attribute
							best_threshold = threshold
		return (best_attribute,best_threshold,splitted)

	def gain(self,unionSet, subsets):
		#input : data and disjoint subsets of it
		#output : information gain
		S = len(unionSet)
		#calculate impurity before split
		impurityBeforeSplit = self.entropy(unionSet)
		#calculate impurity after split
		weights = [len(subset)/S for subset in subsets]
		impurityAfterSplit = 0
		for i in range(len(subsets)):
			impurityAfterSplit += weights[i]*self.entropy(subsets[i])
		#calculate total gain
		totalGain = impurityBeforeSplit - impurityAfterSplit
		return totalGain

	def entropy(self, dataSet):
		S = len(dataSet)
		if S == 0:
			return 0
		num_classes = [0 for i in self.classes]
		for row in dataSet:
			classIndex = list(self.classes).index(row[-1])
			num_classes[classIndex] += 1
		num_classes = [x/S for x in num_classes]
		ent = 0
		for num in num_classes:
			ent += num*self.log(num)
		return ent*-1

	def log(self, x):
		if x == 0:
			return 0
		else:
			return math.log(x,2)

class Node:
	def __init__(self,isLeaf, label, threshold):
		self.label = label
		self.threshold = threshold
		self.isLeaf = isLeaf
		self.children = []