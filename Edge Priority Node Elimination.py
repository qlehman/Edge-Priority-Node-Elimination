'''
Changelog

Aug 14 (additional sort implementation) -> Aug 27 (current)

- mostEdgeLeastTouched no longer sorts by highest removed
  edges when the "--high" flag is used. "--high" now only
  impacts alphanumeric ordering, as intended.

- mostEdgeLeastTouched did not properly add the correct
  node when scanning through edges. This would result in
  some connecting edges adding the examined node to the
  list of connections, rather than the proper connected
  node.
  
- Unfinished comments for mostEdgeLeastTouched were added.
'''

# datetime present exclusively to gauge runtimes
import datetime

# argparse for parsing command line arguments
import argparse

# os for file manipulation
import os

# start time
startTime = datetime.datetime.now()
print(startTime)

'''
Generates a parser with the following arguments:

edgeFile, type: .txt or .csv file
- A text file containing a list of every edge in the graph.
- Each line is of the form "A,B" where A and B are node names.

--nodefile, type: .txt file
- A text file containing a list of names for every node in the graph.
- Each line in the file is a single node name.
- The flag is optional. It must be followed by the file name for the nodes.

--high, optional
- If the flag is used, the sorting will prioritize the highest
- alphanumeric node name when multiple nodes share the same 
- number of edges.
-
- If the flag is missing, it will sort lowest-first instead.

--untouched, optional
- If the flag is used, the sorting will prioritize the node with the 
- least connections to any removed nodes. This occurs prior to 
- the --high flag for breaking ties.

--perline, optional, type: int
- If provided a number >= 1, it will display a number of nodes
- per line in the terminal equal to the value given.
'''
parser = argparse.ArgumentParser()
parser.add_argument("outputFile")
parser.add_argument("edgeFile")
parser.add_argument("--nodefile", action="store")
parser.add_argument("--high", action="store_true")
parser.add_argument("--untouched", action="store_true")
parser.add_argument("--perline", default=5, type=int)
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
            vals = line.rstrip().split(",")
            edge = frozenset(vals)
            edgeSet.add(edge)
    return edgeSet

def nodesAndEdgesFromFile(f):
    edgeSet = set()
    nodeSet = set()
    if os.path.exists(f):
        fo = open(f)
        for line in fo:
            vals = line.rstrip().split(",")
            edge = frozenset(vals)
            nodeSet.add(vals[0])
            nodeSet.add(vals[1])
            edgeSet.add(edge)
    return (nodeSet, edgeSet)


'''
nodePriority takes 2 arguments: nodesEdges, high.

nodesEdges is a tuple containing nodes and edges.

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
def nodePriority(nodesEdges, high):
    nodes = nodesEdges[0]
    edges = nodesEdges[1]
    flipper = -1
    if high:
        flipper = 1

    retOrder = []
    while nodes:
        nodeEdgeCount = {}
        for node in nodes:
            nodeEdgeCount[node] = 0
        for edge in edges:
            for node in edge:
                if node in nodeEdgeCount:
                    nodeEdgeCount[node] += 1

        maxEdge = (sorted(nodeEdgeCount.items(), key=lambda item: (flipper*item[1], item[0]), reverse=high))[0][0]
        nodes.remove(maxEdge)
        edges = [edge for edge in edges if not maxEdge in edge]
        retOrder.append(maxEdge)
    return retOrder

'''
mostEdgeLeastTouched takes two arguments: nodesEdges, high

This is an altered version of nodePriority (above).
It is used when the optional flag "--untouched" is used.

The following changes are made compared to nodePriority:

a) There is another dictionary, which is not reset upon
  selecting a node, that tracks how many edges a given
  node has such that the edge's other node was already
  selected.
b) The dictionary that used to track the number of edges
  still connected to a node now has a list of the nodes
  these remaining edges connect to.
c) After sorting by the number of remaining edges, an
  additional sort is performed based on the new dictionary
  from (a). A node with fewer edges connecting to already
  selected nodes will always be selected first between
  nodes of the same number of remaining edges. This is
  regardless of the "--high" flag being used.

NOTE: If sorting by the most number of removed edges
is deemed useful behavior, adding a circumstantial flag
would be awkward. 

It would likely require either:
a) two flags, such that both call this function independently,
  but change the order of this additional sort
b) two flags, such that the second is useless without calling
  the current "--untouched" flag as well, to dictate the sort order
c) tying together this sort order with the alphanumeric order.

(c) was unintentional behavior prior and would be easiest to implement
simply by removing the check for the "--high" flag -- removing the
"-1*flipper*" preceding the "adjCount[item[0]]" below.

'''
def mostEdgeLeastTouched(nodesEdges, high):
    nodes = nodesEdges[0]
    edges = nodesEdges[1]
    high
    flipper = -1
    if high:
        flipper = 1

    retOrder = []
    adjCount = {}
    for node in nodes:
        adjCount[node] = 0
        
    while nodes:
        nodeEdgeList = {}
        for node in nodes:
            nodeEdgeList[node] = []
        for edge in edges:
            for node in edge:
                nodeEdgeList[node].append(list(set(edge).difference({node}))[0])

        maxEdge = (sorted(nodeEdgeList.items(), key=lambda item: (flipper*len(item[1]), -1*flipper*adjCount[item[0]], item[0]), reverse=high))[0][0]

        for touch in nodeEdgeList[maxEdge]:
            adjCount[touch] += 1

        nodes.remove(maxEdge)
        edges = [edge for edge in edges if not maxEdge in edge]
        retOrder.append(maxEdge)
    return retOrder


'''
output takes no arguments.

1. An empty list for the node order, retOrder, is created.

2. The function determines whether a node file was provided.
--2a. If a node file was provided, it calls nodesFromFile and
------ edgesFromFile using the appropriate command line arguments
------ as a tuple for nodePriority.
--2b. If no node file was provided, it calls nodesAndEdgesFromFile
------ as the tuple argument for nodePriority.
---- In both cases, the "--high" flag is included as an argument
---- for node priority. Both also output nodePriority to retOrder.

3. Terminal and file output are handled together after opening the
output file as per the command line argument.
---- A string, outStr, a bool, first, and an int, num, are created
---- with base values. These are used for the terminal output.
---- For each node in retOrder, the following occurs:
--3a. The node name is written to a new line in the output file.
--3b. The node name is added to outStr as per the following rules:
----3bI. If num is equal to the number provided by "--perline", a
-------- newline character is added to outStr and num is set to 0.
----3bII. Else, if first is false, " -> " is added to outStr.
----3bIII. The node name is added to outStr.
----3bIV. num is incremented.
----3bV. first is set to false.
--3c. outStr is printed to the terminal.

---- As such, if "--perline" were equal to 5, an output may look like:
nodeA -> nodeB -> nodeC -> nodeD -> nodeE
nodeF -> nodeG -> nodeH

'''
def output():
    retOrder = []

    if args.nodefile:
        tupNE = (nodesFromFile(args.nodefile), edgesFromFile(args.edgeFile))
    else:
        tupNE = nodesAndEdgesFromFile(args.edgeFile)

    if args.untouched:
        retOrder = mostEdgeLeastTouched(tupNE, args.high)
    else:
        retOrder = nodePriority(tupNE, args.high)

    outStr = ""
    first = True
    num = 0
    with open(args.outputFile, 'w', newline='') as outF:
        for each in retOrder:
            outF.write(each + "\n")
            if num == args.perline:
                outStr += "\n"
                num = 0
            elif not first:
                outStr +=" -> "
            outStr += each
            num += 1
            first = False
        print(outStr)

'''
multiRun takes one argument: n.

n is an integer, assumed to be positive.

1. output() (above) is called n times.
---- datetime is used to acquire both the start
---- and end times of each run. These deltas are
---- accumulated and then divided by n, to get
---- the average run time per call of output().
'''
def multiRun(n):
    totTime = datetime.timedelta()
    for i in range(n):
        start = datetime.datetime.now()
        output()
        totTime += datetime.datetime.now() - start
    print(totTime/n)

output()

# end time
endTime = datetime.datetime.now()
print(endTime)
#delta time
print(endTime - startTime)

# test for speed
#multiRun(10000)
