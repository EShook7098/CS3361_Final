# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 13:12:58 2020

@author: Ethan
"""

import sys
import getopt as go
import time

#Memory reduction
#We are going to make a Python class utlizing __slots__ to significantly reduce 
#the memory required for keeping track of the following
#A: Storing a cells current state. '.' or 'O'
#B: Storing the count of its neighbors
#C: Storing its next state based on the prior two values

#Also will support class functions - efficiency of these is to be seen


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
    
        

def Error(msg):
    print(msg)
    sys.exit(1)

def GetMatrix(filepath):
    lines = GetLines(filepath)
    return ParseLines(lines, filepath)
        
def GetLines(filepath):
    file = open(filepath, 'r')
    lines = file.readlines()
    file.close()
    return lines

def RemakeInt(cellValue):
    if cellValue == 'O':
        return 1
    else:
        return 0

def AllocateEmpty(width, height, adjust):
    arr = [None] * (height + adjust)
    for i in range(height + adjust):
        arr[i] = [None] * (width + adjust)
        
    return arr

def ParseLines(lines, filepath): #Use mmap CAREFULLY to read in a large file?
    width = len(lines[0]) - 1
    height = len(lines)
    print("Read in length: " + str(width))
    print("Lines: " + str(height))
    #charMatrix = np.empty((dim, dim), dtype = str)
    #matrix = np.empty((dim, dim), dtype = int)
    #matrix = AllocateEmpty(dim)
    matrix = AllocateEmpty(width, height, 2)
    print(matrix)
    validChars = ['.', 'O', '\n']
    rowNum = 1
    countTime = time.time()
    for line in lines:
        print(rowNum)
        for colNum in range(0, width):
            char = line[colNum]
            
            #print(rowNum, colNum)
            if char not in validChars:
                Error("Error: Invalid character detected in file.\nInvalid character was: '" + char + "'")
                #We are storing tuples to prevent the cost of another full array for checking counts.
                #Instead we'll store counts of living cells alongside the tuple
            matrix[rowNum][colNum + 1] = Cell(char, None)
             #- Effect on time is negligible: Total: ~0.25s - Adds +~.2 seconds
            #charMatrix[rowNum, colNum] = char
        rowNum += 1
        
    print("Size of cell : " + str(sys.getsizeof(matrix[1][1])))
    print("Read time: " + str(time.time() - countTime))
    return matrix, lines 
  
def ExtractCellState(matrix):    
    width = len(matrix[0]) - 1 #More like.. position ending col without wrap of the appended final col
    height = len(matrix)  - 1
    writeMatrix = AllocateEmpty(width - 1, height - 1, 0)
    print(len(writeMatrix), len(writeMatrix[0]))
    for row in range(1, height):
        for col in range(1, width):
            writeMatrix[row - 1][col - 1] = matrix[row][col].state
            
    return writeMatrix

def WriteMatrix(matrix, outputPath):
    writeMatrix = ExtractCellState(matrix)
    print(writeMatrix)
    with open(outputPath, 'w') as file:
        for line in writeMatrix:
            file.write("".join(line) + "\n")
    file.close()    
  
    
  
def SetCorners(matrix, height, width):
    #print("Position : " + str(height + 1) + ", " + str(width))
    matrix[0][0] = matrix[height - 1][width - 1] #Get lower right, set upper left
    matrix[0][width] = matrix[height-1][1]
    matrix[height][0] = matrix[1][width-1]
    matrix[height][width] = matrix[1][1]
    
def SetCols(matrix, height, width):
    for rowIndex in range(1, height):
        matrix[rowIndex][0] = matrix[rowIndex][width - 1]
        
    for rowIndex in range(1, height):
        matrix[rowIndex][width] = matrix[rowIndex][1]
        
def ExpandBorders(matrix):
    width = len(matrix[0]) - 1
    height = len(matrix)  - 1#Get outer 
    SetCorners(matrix, height, width)
    matrix[0][1:width] = matrix[height - 1][1:width]
    matrix[height][1:width] = matrix[1][1:width]
    SetCols(matrix, height, width)

#Automatically updates border regions as they are already pointers to the inner sections. 
#OH WHAT A DAY! WHAT A LOVELY DAY - https://www.youtube.com/watch?v=2z2PKwLPrC0
def SetNextIteration(matrix):
    dim = len(matrix) - 1 #Get outer indice
    
    for row in range(1, dim):
        for col in range(1, dim):
            matrix[row][col].SetNextIteration()

def SetNextState(matrix, rowIndex, colIndex, neighborSet):
    count = 0
    for set in neighborSet:
        if(matrix[rowIndex + set[0]][colIndex+set[1]].state == 'O'):
            count +=1

    matrix[rowIndex][colIndex].SetNextState(count)

def ConvolveKinda(matrix):
    height = len(matrix) - 1 #Get outer indice
    width = len(matrix[0]) - 2
    print("Height: " + str(height) + " Width: " + str(width))
    neighborSteps = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    
    for row in range(1, height):
        for col in range(1, width):
            SetNextState(matrix, row, col, neighborSteps)

def PrintExpandedMatrix(matrix):
    width = len(matrix[0])
    height = len(matrix)
    print("-------------------")
    print("Matrix dimensions: " + str(height) + "x" + str(width))
    for row in range(0, height):
        print()
        for col in range(0, width):
            print(matrix[row][col].state, end = "")
            
    print("\n")
    print("-------------------")   

def PrintMatrix(matrix):
    width = len(matrix[0]) - 1
    height = len(matrix)  - 1
    print("-------------------")
    print("Matrix dimensions: " + str(height - 1) + "x" + str(width - 1))
    for row in range(1, height):
        print()
        for col in range(1, width):
            print(matrix[row][col].state, end = "")
            
    print("\n")
    print("-------------------")

#If the outer edge can be pointing to the same inner memory locations.. that'd be FUCKING awesome


if __name__ == '__main__':
    startTime = time.time()
    start = time.time()
    print("Project :: 11469438")
    
    inputPath = -1
    outputPath = -1
    threads = 1
    
    opts, args = go.getopt(sys.argv[1:], 'i:o:t:', ['inputPath =', 'outputPath =', 'threads'])
    
    for opt, arg in opts:
        if opt in ['-i', '--inputPath']:
            inputPath = arg
        elif opt in ['-o', '--outputPath']:
            outputPath = arg
        elif opt in ['-t', '--threads']:
            threads = int(arg)
            
    if inputPath == -1:
        Error("Error: Path to input file not provided.")
    elif outputPath == -1:
        Error("Error: Path to output file not provided.")
    elif not (threads > 0):
        Error("Error: Number of threads must be greater than zero.")
        
    matrix, lines = GetMatrix(inputPath) 
    start = time.time()
    
    ExpandBorders(matrix)
    
    #ConvolveKinda(matrix)
    #SetNextIteration(matrix)
    
    
    print("Expansion: " + str(time.time() - start))
    for i in range(100):
        ConvolveKinda(matrix)
        SetNextIteration(matrix)
        
    PrintExpandedMatrix(matrix)
    PrintMatrix(matrix)
    WriteMatrix(matrix, outputPath)
    print(f"{inputPath}, {outputPath}, {threads}")
    print("Total Execution Time: " + str(time.time() - start))
    
    
    #time_step_0.dat
    #10_10_matrix.txt 