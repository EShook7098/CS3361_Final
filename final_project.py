# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 11:39:51 2020

@author: Ethan
"""

import sys
import getopt as go
import numpy as np
import scipy as sp
import scipy.signal
#import scipy.ndimage as image
from dataclasses import dataclass
#import collections as c
import time
#import copy
import math
#import skimage
#from skimage.util.shape import view_as_windows
#from skimage.util.shape import view_as_blocks
from multiprocessing import Process
from multiprocessing import Pool

@dataclass
class ThreadArgs:
    matrix: np.array
    dim: int
    #Which rows should we actually keep? Where do they map to?
    ymin: int
    ymax: int



def Error(msg):
    print(msg)
    sys.exit(1)

##################
# Read In Matrix #
##################

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

def ParseLines(lines, filepath): #Use mmap CAREFULLY to read in a large file?
    dim = len(lines[0]) - 1
    charMatrix = np.empty((dim, dim), dtype = str)
    matrix = np.empty((dim, dim), dtype = int)
    validChars = ['.', 'O', '\n']

    rowNum = 0
    countTime = time.time()
    for line in lines:
        for colNum in range(0, dim):
            char = line[colNum]

            #print(char, colNum)

            if char not in validChars:
                Error("Error: Invalid character detected in file.\nInvalid character was: '" + char + "'")

             #- Effect on time is negligible: Total: ~0.25s - Adds +~.2 seconds
            charMatrix[rowNum, colNum] = char

        rowNum += 1
    print("Read time: " + str(time.time() - countTime))

    #I love convolve, convolve hates characters - Vectorize alterations for efficiency
    RemakeMatrix = np.vectorize(RemakeInt)
    matrix = RemakeMatrix(charMatrix)
    print("Alteration Time: " + str(time.time() - countTime))
    return ThreadArgs(matrix, dim, 0, dim)


#######################
# Simulate Time Steps #
#######################

def SetCell(cellValue, countValue):
    print()
    if (cellValue == 0 and (countValue > 0 and countValue % 2 == 0)) or (cellValue == 1  and (countValue) >= 2 and countValue <= 4):
        return 1
    else:
        return 0

def ProcessCells(matrix, filterMatrix, SetMatrixCell):

    #dim = threadArgs.dim
    #matrix = threadArgs.matrix
    print(matrix)


    #countTime = time.time()
    counts = scipy.signal.convolve2d(matrix, filterMatrix, mode = 'same', boundary = 'wrap')
    #print("Iteration: " + str(iteration) + " | Count time: " + str(time.time() - countTime))

    #matrix[:] = SetMatrixCell(matrix.flatten(), counts.flatten()).reshape([dim, dim])[:]
    matrix[:] = SetMatrixCell(matrix, counts)[:]

    #print("Iteration time: " + str(time.time() - countTime))
    return matrix

    #threadArgs.matrix[:] = matrix[:] #Copy modified matrix into the memory location
def CombineCells():
    pass



def Remake(cellValue):
    if cellValue == 1:
        return 'O'
    else:
        return '.'

def CreateRandomMatrix(dim):
    matrix = np.random.choice(2, [dim, dim])
    charMatrix = np.empty([dim, dim], dtype = str)
    RemakeMatrix = np.vectorize(Remake)

    #charMatrix = RemakeMatrix(matrix, charMatrix)

    return ThreadArgs(matrix, dim, 0, dim)

def WriteMatrix(matrix, outputPath):
    RemakeMatrix = np.vectorize(Remake)
    charMatrix = np.empty(matrix.shape, dtype = str)
    charMatrix = RemakeMatrix(matrix)
    with open(outputPath, 'wb') as file:
        np.savetxt(file, charMatrix, delimiter='', newline='\n', fmt  ='%s')
    file.close()

########
# Main #
########




if __name__ == '__main__':


    startTime = time.time()
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

    print(f"{inputPath}, {outputPath}, {threads}")


    threadArgs = GetMatrix(inputPath)
    #threadArgs = CreateRandomMatrix(1000)
    #if threads == 1:
        #for index in range(1):
            #rocessCells(threadArgs)
        #pass
    #else:
        #threadArgArray = DivideThreadArgs(threadArgs, threads) #Operates off of memory location, no return
    filterMatrix = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype = int)
    SetMatrixCell = np.vectorize(SetCell)
    matrix = threadArgs.matrix
    #SERIOUSLY FUCK OVERLAP
    #counts = scipy.signal.convolve2d(matrix, filterMatrix, mode = 'same', boundary = 'wrap')
    #countsArray = np.split(counts, threads)
    #matrixArray = np.split(matrix, threads)



    if threads == 1:
        print("here")
        for iteration in range(1):
            counts = scipy.signal.convolve2d(matrix, filterMatrix, mode = 'same', boundary = 'wrap')
            matrix[:] = SetMatrixCell(matrix, counts)[:]
    else:
        print("there")
        process_pool = Pool(threads)
        for iteration in range(10):
            results = []
            data = []
            counts = scipy.signal.convolve2d(matrix, filterMatrix, mode = 'same', boundary = 'wrap')
            countsArray = np.split(counts, threads)
            matrixArray = np.split(matrix, threads)
            for thread in range(threads):
                data.append((matrixArray[thread], countsArray[thread]))
                output = process_pool.starmap(SetMatrixCell, data)
            #process_pool.join()
            matrix = np.concatenate(output)


        process_pool.close()
    print(time.time() - startTime)
    # for thread in range(threads):
    #     print(str(thread))
    #     p = Process(target = SetMatrixCell, args =(countsArray[thread], matrixArray[thread],))
    #     jobs.append(p)
    #     p.join()
    #print(output)

    # p2 = Process(target = SetMatrixCell, args =(countsArray[1], matrixArray[1],))

    # p1.start()
    # p2.start()

    # p1.join()
    # p2.join()
    #print(threadArgs.matrix)
    #ProcessCells(threadArgs)
    WriteMatrix(matrix, outputPath)

    #print("------------------------------")
    #print(matrix)

    #
