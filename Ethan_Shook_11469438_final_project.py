# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 13:12:58 2020

@author: Ethan
"""

import sys
import getopt as go
import time
from multiprocessing import Pool, Array
#from multiprocessing import shared_memory, Process, Lock, cpu_count, current_process
i#mport multiprocessing
from Cell import ConvolveKinda, Cell, SetNextState
from copy import deepcopy


#Memory reduction
#We are going to make a Python class utlizing __slots__ to significantly reduce
#the memory required for keeping track of the following
#A: Storing a cells current state. '.' or 'O'
#B: Storing the count of its neighbors
#C: Storing its next state based on the prior two values

#Also will support class functions - efficiency of these is to be seen



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
    return matrix

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
    return WriteMatrix


def SetNextIteration(matrix):
    height = len(matrix) - 1#Get outer indice
    width = len(matrix[0]) - 1

    for row in range(1, height):
        for col in range(1, width):
            print(row, col)
            matrix[row][col].SetNextIteration()


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
    print(height, width)
    print("-------------------")
    print("Matrix dimensions: " + str(height - 1) + "x" + str(width - 1))
    for row in range(1, height):
        print()
        for col in range(1, width):
            print(matrix[row][col].state, end = "")

    print("\n")
    print("-------------------")


def SplitMatrix(matrix, threads):
    increment, remainder = divmod(len(matrix), threads)
    matrixArray = AllocateEmpty(1, threads, 0)

    stop = (0 + 1) * increment + min(0 + 1, remainder)
    print("Thread {} Start: {} End {}".format(0, 0, stop))
    matrixArray[0] = matrix[0:stop + 1][:]

    for sectionNum in range(1, threads - 1):
        start = sectionNum * increment + min(sectionNum, remainder) - 1
        stop = (sectionNum + 1) * increment + min(sectionNum + 1, remainder)
        print("Thread {} Start: {} End {}".format(sectionNum, start, stop))
        matrixArray[sectionNum] = matrix[start:stop + 1][:]


    sectionNum = threads - 1
    start = sectionNum * increment + min(sectionNum, remainder) - 1
    stop = (sectionNum + 1) * increment + min(sectionNum + 1, remainder) - 1
    print("Thread {} Start: {} End {}".format(sectionNum, start, stop))
    matrixArray[threads - 1] = matrix[start:stop + 1]
    return matrixArray

#def ReattachMatrices(matrixArray):

    #for matrix in range(len(matrixArray)):

#If the outer edge can be pointing to the same inner memory locations.. that'd be FUCKING awesome

def JoinMatrices(matrix, matrixArray):
    #print("JOINING")
    #print(len(matrixArray))
    row = 1
    #print("start")
    for matriceRow in matrixArray[0][1:-1]:
        col = 1
        for cell in matriceRow[1:-1]:
            #print(matrix[row][col].state, end = "")
            matrix[row][col].UpdateSelf(cell)
            col += 1
        #print("\n")
        row +=1
    #print("\n")

    for matrice in matrixArray[1:-1]:
        #print("mid")
        for matriceRow in matrice[1:-1]:
            col = 1
            for cell in matriceRow[1:-1]:
                #print(matrix[row][col].state, end = "")
                matrix[row][col].UpdateSelf(cell)
                col += 1
            #print("\n")
            row +=1
    #print("\n")
    #print("end")
    for matriceRow in matrixArray[-1][1:-1]:
        col = 1
        for cell in matriceRow[1:-1]:
            #print(matrix[row][col].state, end = "")
            matrix[row][col].UpdateSelf(cell)
            col += 1
        #print("\n")
        row +=1

if __name__ == '__main__':
    startProgram = time.time()
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




    matrix = GetMatrix(inputPath)

    #ExpandBorders(matrix)
    #matrixArray = SplitMatrix(matrix, threads)


    #ConvolveKinda(matrixArray[0])
    #ConvolveKinda(matrixArray[1])
    #SetNextIteration(matrixArray[0])
    #SetNextIteration(matrixArray[1])
    PrintMatrix(matrix)

    if threads > 1:
        ExpandBorders(matrix)
        matrixArray = SplitMatrix(matrix, threads)


        data = []
        for index in range(threads):
            data.append(matrixArray[index])
            #print("Matrix Array {} Length is {}".format(index,len(matrixArray[index])))

        process_pool = Pool(threads)
        for i in range(100):
            output = process_pool.map(ConvolveKinda, data)
            JoinMatrices(matrix, output)
            #SetNextIteration(matrix)

            #print("END OF ITERATION")
            #PrintMatrix(matrix)
            #PrintExpandedMatrix(matrix)


        process_pool.close()
        process_pool.join()
    else:
        ExpandBorders(matrix)
        for i in range(100):
            ConvolveKinda(matrix)
            SetNextIteration(matrix)

     #Beauty of it all being memory references



        #PrintMatrix(matrix)
        #PrintExpandedMatrix(matrix)

    #matrixArray = SplitMatrix(matrix, threads)

    #PrintExpandedMatrix(matrix)
    #PrintMatrix(matrix)
    WriteMatrix(matrix, outputPath)
    #print(f"{inputPath}, {outputPath}, {threads}")
    print("Total Execution Time: " + str(time.time() - startProgram))


    #time_step_0.dat
    #10_10_matrix.txt
