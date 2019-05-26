# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 12:17:45 2019

@author: Cullen
"""

from copy import deepcopy
import time

def pList(l):
    for i in l:
        print("{}:".format(i), l[i])
    print()

def recCount(neighborList, currVert = None):
    count = 0
    if currVert == None:
        for vertex in neighborList:
            count += recCount(deepcopy(neighborList), vertex)
        return count
    else:
        oList = deepcopy(neighborList)
        if len(neighborList[currVert]) == 0:
            for i in neighborList:
                if len(neighborList[i]) != 0:
                    return 0
            return 1
        for path in oList[currVert]:
            neighborList[currVert].remove(path)
            neighborList[path].remove(currVert)
            count += recCount(deepcopy(neighborList), path)
            neighborList = deepcopy(oList)
        return count
    
def genNeighborList(cycle):
    neighborList = {}
    for i in range(len(cycle)-1):
        if i == 0:
            neighborList[cycle[0]] = [cycle[1]]
            neighborList[cycle[1]] = [cycle[0]]
            continue
        try:
            neighborList[cycle[i]].append(cycle[i+1])
        except KeyError:
            neighborList[cycle[i]] = [cycle[i+1]]
        try:
            neighborList[cycle[i+1]].append(cycle[i])
        except KeyError:
            neighborList[cycle[i+1]] = [cycle[i]]
    return neighborList

def output(cycle):
    neighborList = genNeighborList(cycle[1:])
    sTime = time.time()
    count = recCount(deepcopy(neighborList), cycle[1]) * 2 * (len(cycle) - 1)
    fTime = time.time()
    return count, (fTime-sTime)

if __name__ == "__main__":
    cycle = input("Cycle: ")
    neighborList = genNeighborList(cycle[1:])
    sTime = time.time()
    count = recCount(deepcopy(neighborList), cycle[1]) * 2 * (len(cycle) - 1)
    fTime = time.time()
    print(count)
    print(fTime - sTime)