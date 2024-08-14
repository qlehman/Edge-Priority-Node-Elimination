'''
Changelog

Aug 10 (init) -> Aug 14 (current)

- Added a command line argument for the output file (required).
-- There is no explicitly required filetype, but the script
    anticipates a text file or something that functions as such
    per python's file writing.

- The node file command line argument is no longer required.
-- It is now a flag, "--nodeFile".
-- If no node file is provided, the script will automatically
    generate the list of nodes based off of the edge file.
-- Inclusion of a node file would retain the old functionality
    of marking some graph nodes as unable to be eliminated
    (by only representing them in the edge file).

- Added a command line flag, "--perline", to dictate how many
    nodes are displayed per line in the terminal output.
-- The default value is 5.

- Refined terminal output to something easier to read
-- It is now of the form "nodeA -> nodeB -> nodeC..."

- Added a new function, nodesAndEdgesFromFile(f)
-- f is a string containing the file path to the chosen file.
-- This is used when no node file is provided to generate
    the node list, as mentioned above.

- Added a new function, output()
-- This function determines which file read functions
    to call based on provided arguments.
-- It prints the node elimination order into the terminal
    as per the --perline flag and the format stated above.
-- It also stores the nodes, one per line, into the output
    file.

- Added a new functiion, multirun(n)
-- This function loops n times, running output() once
    per loop.
-- It also makes use of datetime to gather the total
    runtime of each call to output(), then averages
    the time taken.
-- This is a utility function for testing runtimes
    of the bulk of the computations.

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
parser.add_argument("outputFile")
parser.add_argument("edgeFile")
parser.add_argument("--nodeFile", required=False)
parser.add_argument("--high", default="false", type=str)
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
def nodePriority(nodesEdges, high):
    nodes = nodesEdges[0]
    edges = nodesEdges[1]
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

        maxEdge = next(iter(dict(sorted(nodeEdgeCount.items(), key=lambda item: (flipper*item[1], item[0]), reverse=flip)).keys()))
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
    if args.nodeFile:
        retOrder = nodePriority((nodesFromFile(args.nodeFile), edgesFromFile(args.edgeFile)), args.high)
    else:
        retOrder = nodePriority(nodesAndEdgesFromFile(args.edgeFile), args.high)
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
