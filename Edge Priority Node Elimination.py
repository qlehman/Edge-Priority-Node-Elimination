# datetime present exclusively to gauge runtimes
import datetime

# argparse for parsing command line arguments
import argparse

# os for file manipulation
import os

# start time
print(datetime.datetime.now())

'''
Generates a parser with the following arguments:

nodeFile, type: .txt file
- A text file containing a list of names for every node in the graph.
- Each line in the file is a single node name.

edgeFile, type: .txt or .csv file
- A text file containing a list of every edge in the graph.
- Each line is of the form "A,B" where A and B are node names.

--high, optional, type: string
- If provided any value (such as "--high=true") in the command line,
- the sorting will prioritize the highest alphanumeric node name
- when multiple nodes share the same number of edges.
-
- If the flag is missing or set to "--high=false"), it will sort
- lowest-first instead.
'''
parser = argparse.ArgumentParser()
parser.add_argument("nodeFile")
parser.add_argument("edgeFile")
parser.add_argument("--high", default="false", type=str)
args = parser.parse_args()

'''
1. Creates an empty set, nodeSet.

2. If the provided file -- f -- exists,
---- Iterates each line of the file.
---- Strips each line of the newline character.
---- Adds the text of the line to nodeSet.

3. Returns nodeSet. It may be empty.

As a set is used, multiple instances of the same
node name will not be entered multiple times.

This is to increase flexibility for human or
programmatic errors.

Assuming nodes are each named uniquely allows
for the code to ignore duplicate lines in the
provided file.
'''
def nodesFromFile(f):
    nodeSet = set()
    if os.path.exists(f):
        fo = open(f)
        for line in fo:
            nodeSet.add(line.rstrip())
    return nodeSet

'''
1. Creates an empty set, edgeSet.

2. If the provided file -- f -- exists,
---- Iterates each line of the file.
---- Strips each line of the newline character.
---- Splits the line into a list, using "," as a delimiter.
---- Converts the list to a frozen set.
---- Adds the frozen set to edgeSet.

3. Returns edgeSet. It may be empty.

As with nodesFromFile, edgesFromFile uses sets
so that duplicate instances of edges are only
ever counted once.

This means two lines, "A,B", and "B,A", which
ultimately refer to the same edge will only
be counted once.

A frozen set is immutable after creation.
'''
def edgesFromFile(f):
    edgeSet = set()
    if os.path.exists(f):
        fo = open(f)
        for line in fo:
            edge = frozenset(line.rstrip().split(","))
            edgeSet.add(edge)
    return edgeSet


'''
nodePriority takes 3 arguments: nodes, edges, high.

nodes is a set, as per the output of nodesFromFile,
which contains every node present in the graph.

edges is a set of sets, as per the output of edgesFromFile,
which contains every edge present in the graph.
Each edge is of the form {A,B}, where A and B are the
nodes the edges connect.

high is directly pulled from the argument parser's --high.
It is explained in the parser's comments.

1. A boolean value (flip) and integer (flipper) are
created based on the value of high.
---- These values are used when sorting to change priority
---- when multiple nodes have the same edge count
---- (as explained in the parser comments).

2. The list of nodes are looped, popping the node with
the highest number of edges at the end of each cycle.

--2a. A dictionary, nodeEdgeCount, is created.
------ The keys are each node name yet to be selected.
------ The values are updated to reflect the number of
------ remaining edges the node has.

--2b. For every edge yet to be removed,
------ Increments each component node's dictionary
------ value by 1.

--2c. nodeEdgeCount is then sorted.
------ Regardless of the value of high, the primary
------ sorting is the node with the highest number
------ of edges.
------ If high is true, then it will prioritize nodes
------ of higher alphanumeric values in ties.
------ Otherwise, it prioritizes the lowest.

--2d. The node with the highest value is removed
------ from the node set.

--2e. Each edge the removed node shared is removed
------ from the edge set.

--2f. The removed node is added to the return list.

This continues until no nodes remain in the node list.

This does not guarantee that the edge list will be empty
as well unless it is assumed that the edge list does not
contain a reference to a node that does not exist in the
node list.
'''
def nodePriority(nodes, edges, high):
    flip = (high.lower() == "true")
    flipper = -1
    if flip:
        flipper = 1

    retOrder = []
    while nodes:
        nodeEdgeCount = {}
        for node in nodes:
            nodeEdgeCount[node] = 0
        for edge in edges:
            for node in edge:
                nodeEdgeCount[node] += 1

        maxEdge = list(dict(sorted(nodeEdgeCount.items(), key=lambda item: (flipper*item[1], item[0]), reverse=flip)).keys())[0]
        nodes.remove(maxEdge)
        edges = [edge for edge in edges if not maxEdge in edge]
        retOrder.append(maxEdge)
    return retOrder

print(nodePriority(nodesFromFile(args.nodeFile), edgesFromFile(args.edgeFile), args.high))
print(datetime.datetime.now())