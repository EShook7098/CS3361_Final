# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 13:26:27 2020

@author: Ethan
"""
import time

class Cell:
    __slots__ = 'state', 'nCount', 'nextState'

    def __init__(self, s, ns):
        self.state = s
        self.nextState = ns


    def SetNextIteration(self):
        self.state = self.nextState
        self.nextState = None

    def SetNext(self, cellValue):
        self.nextState = cellValue


def GetNextState(cellValue, count):
    if (cellValue == '.' and (count > 0 and count % 2 == 0)) or (cellValue == 'O' and count >= 2 and count <= 4):
        return 'O'
    else:
        return '.'

def SetNextState(flatNeighbors, char):
    count = 0
    #print(char)
    #print(flatNeighbors)
    for neighbor in flatNeighbors:
        #print("State " + str(neighbor.state) + " | ", end = "")
        if neighbor.state == 'O':
            count += 1
    #test = GetNextState(char[0], count)
    print(count, char)
    #print(test)
    return GetNextState(char, count)

def ConvolveKinda(matrix, neighborSteps):
    start = time.time()

    return SetNextState(matrix, row, col, neighborSteps)

    #print("Convolved in: " + str(time.time() - start))
    #x.value += time.time() - start
