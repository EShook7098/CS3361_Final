# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 13:26:27 2020

@author: Ethan
"""
import time

##############
# Cell Class #
##############

#Memory reduction
#We are going to make a Python class utlizing __slots__ to significantly reduce
#the memory required for keeping track of the following
#A: Storing a cells current state. '.' or 'O'
#B: Storing its next state 

#Ultimately failed as python either hates copying objects or memory references. Best approach is to use two shared arrays, as each thread will only write a portion.

class Cell:
    __slots__ = 'state', 'nCount', 'nextState'

    def __init__(self, s, ns):
        self.state = s
        self.nextState = ns

    def SetNextState(self, nCount):
        if (self.state == '.' and (nCount > 0 and nCount % 2 == 0)) or (self.state == 'O' and nCount >= 2 and nCount <= 4):
            self.nextState = 'O'
        else:
            self.nextState = '.'

    def SetNextIteration(self):
        self.state = self.nextState
        self.nextState = None

    def UpdateSelf(self, Cell):
        self.state = Cell.nextState

#####################
# Convolution - ish #
#####################

#Check each neighbor and get a count of living neighbors
def SetNextState(matrix, rowIndex, colIndex, neighborSet):
    count = 0
    for set in neighborSet:
        if(matrix[rowIndex + set[0]][colIndex+set[1]].state == 'O'):
            count += 1

    matrix[rowIndex][colIndex].SetNextState(count)

#Check each neighbor for every cell non-border in the passed matrix
def ConvolveKinda(matrix, neighborSteps):
    start = time.time()
    height = len(matrix) - 1 #Get outer indice
    width = len(matrix[0]) - 1

    for row in range(1, height):
        for col in range(1, width):
            SetNextState(matrix, row, col, neighborSteps)

    print("Convolved in: " + str(time.time() - start))
    return matrix
