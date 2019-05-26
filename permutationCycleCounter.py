# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 09:27:23 2019

@author: Cullen
"""
from collections import defaultdict
from copy import deepcopy
from recursiveCycleCounter import recCount, genNeighborList, output

import numpy as np
import time


class permCount(object):
    def __init__(self, cycle):
        '''
        The first edge is removed because cycles are reversible. So by listing all of the cycles that start with edge e and ending
        with edge E' where E' is the set of edges from V such that E' = V(E) - e, we can reverse all of those cycles to obtain all 
        of the cycles starting with some edge in E' and ending with e to obtain a list of cycles C beginning at V.
        
        Next, due to the nature of a cycle, the cycle can be started from any other vertex within a given cycle c, and by following
        the same path, obtain a new cycle c'. Because the list obtained in the paragraph above, C, contains all cycles beginning at
        V it follows that by using a left-shift algorithm and replacing the new LSB with the new MSB we will obtain a list of all 
        cycles in G.
        
        For example in the K3 graph:
            All cycles beginning with the edge 0->1, e:
                0120
            Reverse that cycle to obtain all cycles beginning with E' and ending with e:
                0210
            
            C so far:
                0120
                0210
            
            Left-shift cycles in C:
                1201
                2102
            
            Left-shift again:
                2012
                1021
                
            All C in G:
                0120
                0210
                1201
                2102
                2012
                1021
                
        The number of left-shifts required will always be equal to the number of edges in the graph.
        Thus by counting the number of cycles n that begin with some edge e, we can obtain the number of cycles in G by:
            C(G) = 2n * |E|
        '''
        self.adjMat = self.genAdjacencyMatrix(cycle[1:])
        self.depth = 0
        self.currentV = int(cycle[1])
        pass
    
    def genAdjacencyMatrix(self, stringCycle):
        cycle = []
        m = len(stringCycle)
        for item in stringCycle:
            cycle.append(int(item))
        n = max(cycle) + 1 #tells us how many vertices are in the graph. add 1 so numpy works correctly
        
        adjMat = np.zeros((m,n,n)) #adjacency matrix is nxn
        for i in range(len(cycle)-1):
            adjMat[0][cycle[i]][cycle[i+1]] = 1
            adjMat[0][cycle[i+1]][cycle[i]] = 1
        return adjMat
    
    def getDegree(self, vertex):
        return np.sum(self.adjMat[self.depth][vertex])
    

    
    def travelEdge(self, vertexTo):
        vertexFrom = self.currentV #Readability
        self.adjMat[self.depth + 1] = np.copy(self.adjMat[self.depth])
        self.depth += 1
        self.adjMat[self.depth][vertexTo][vertexFrom] = 0
        self.adjMat[self.depth][vertexFrom][vertexTo] = 0
        self.currentV = vertexTo
    
    #Use exclude to exclude some vertex (normally currentV)
    def getNeighborList(self, vertex, exclude = None):
        neighbors = []
        for i in range(self.adjMat.shape[1]):
            if i == exclude:
                continue
            if self.adjMat[self.depth][vertex][i] == 1:
                neighbors.append(i)
        return neighbors
    
    def crossBridge(self, prevVertex, currVertex, originalVertex = None, depth = 0):
        if depth == 0:
            originalVertex = prevVertex
        
#        print('CROSSING BRIDGE', prevVertex, currVertex, originalVertex, depth)
        if self.getDegree(currVertex) == 2 and currVertex != originalVertex:
            where = np.argwhere(self.adjMat[self.depth][currVertex])
            for index in where:
                if index[0] != prevVertex:
                    return self.crossBridge(currVertex, index[0], originalVertex, depth + 1)
        else:
            return currVertex
    
    def neighborSets(self, vertex):
        currNeighbors = self.getNeighborList(vertex)
                
        degreeSort = defaultdict(lambda: list()) #Dictionary key will be degree and contain a list of all vertices with that degree
        for item in currNeighbors:
            degreeSort[self.getDegree(item)].append(item)
        
        for v in degreeSort[2]:
            deg2PathEnd = self.crossBridge(vertex, v)
#            print(v, deg2PathEnd)
            currNeighbors.remove(v)
            if deg2PathEnd not in currNeighbors:
                currNeighbors.append(deg2PathEnd) #Replace the degree 2 vertex with its path end
        
        return set(currNeighbors)
    
    def getSymmetricalNeighbors(self):
        currNeighbors = self.getNeighborList(self.currentV)
                
        degreeSort = defaultdict(lambda: list())
        neighborSetSort = defaultdict(lambda: list()) #Dictionary key will be degree and contain a list of all vertices with that degree
        for item in currNeighbors:
            degreeSort[self.getDegree(item)].append(item)
            neighborSetSort[item] = self.neighborSets(item)
#            print(item, neighborSetSort[item])
#        print(degreeSort)
        symmetry = []
        foundSymmetry = []
        deg2EndPoints = defaultdict(lambda: list())
        for degree in degreeSort:
            
            #Special sort the degree 2 vertices
            if degree == 2:
                for item in degreeSort[2]:
                    try:
                        endPoint = list(neighborSetSort[item] - set([self.currentV]))[0] #If the cycle ends on a point other than currentV
                    except IndexError:
                        endPoint = list(neighborSetSort[item])[0] #If the cycle ends on currentV
                    deg2EndPoints[endPoint].append(item) #Get the endpoints, put them in a dictionary
#                print(deg2EndPoints)
                    
                #Any end points that happen to be currentV, they're all symmetrical. Deal with them now
                if self.currentV in deg2EndPoints:
                    symmetry.append(deg2EndPoints[self.currentV])
                    for item in deg2EndPoints[self.currentV]:
                        foundSymmetry.append(item)
                continue
            
            for i in range(len(degreeSort[degree])):
                v1 = degreeSort[degree][i]
                if v1 in foundSymmetry:
                    continue
                nSet1 = neighborSetSort[v1]
                
                container = [v1]
                if v1 in deg2EndPoints:
                    container += [item for item in deg2EndPoints[v1]]
                    
                for j in range(i+1,len(degreeSort[degree])):
                    
                    v2 = degreeSort[degree][j]
                    if v2 in foundSymmetry:
                        continue
                    nSet2 = neighborSetSort[v2]
                    
                    #This is the function that determines if they're symmetrical
                    if len(nSet1.symmetric_difference(nSet2) - set([v1]) - set([v2])) == 0:
                        container.append(v2)
                        if v2 in deg2EndPoints:
                            container += [item for item in deg2EndPoints[v2]]
                            
                symmetry.append(container)
                for item in container:
                    foundSymmetry.append(item)
        for item in currNeighbors:
            if item not in foundSymmetry:
                symmetry.append([item])
        return symmetry
        
    
    def countCycles(self, currMult = 0):
#        print(self.currentV)
#        print(self.adjMat[self.depth])
#        print(self.getSymmetricalNeighbors())
##        raise Exception('break')
#        input()
        currMult = -1
        self.adjMat[self.depth][1] += 10
        
        result = 0
        if currMult == 0:
            symmVerts = self.getSymmetricalNeighbors()
            for symmGroup in symmVerts:
                previousV = deepcopy(self.currentV)
                self.travelEdge(symmGroup[0])
                result += self.countCycles(len(symmGroup))
                self.depth -= 1
                self.currentV = previousV
            result *= 2 * self.adjMat.shape[0]
            return result
        elif np.sum(self.adjMat[self.depth]) != 0 and self.getDegree(self.currentV) == 0:
            return 0
#        elif np.sum(self.adjMat[self.depth]) != 0:
#            symmVerts = self.getSymmetricalNeighbors()
#            for symmGroup in symmVerts:
#                previousV = deepcopy(self.currentV)
#                self.travelEdge(symmGroup[0])
#                result += self.countCycles(len(symmGroup) * currMult)
#                self.depth -= 1
#                self.currentV = previousV
#            return result
        elif np.sum(self.adjMat[self.depth]) == 0:
            return currMult
        else:
            raise Exception("SOMETHING WENT WRONG")
                
        
if __name__ == '__main__':
    i = input('Cycle: ')
    p = permCount(i)
    s = time.time()
    r = p.countCycles()
    f = time.time()
    print('Permutation Result:', r)
    print('Permutation Time:', f-s)
    
    count, time = output(i)
    print('\nBrute Force Result:', count)
    print('Brute Force Time:', time)
    
    
 