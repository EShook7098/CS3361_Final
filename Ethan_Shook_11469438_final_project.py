# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 13:12:58 2020

@author: Ethan
"""

import sys
import getopt as go
from multiprocessing import Pool
from Cell import ConvolveKinda, Cell, SetNextState
import time

#Displays Error messages
def Error(msg):
    print(msg)
    sys.exit(1)

#############
# Read File #
#############

#Get the matrix
def GetMatrix(filepath):
    lines = GetLines(filepath)
    return ParseLines(lines, filepath)

#Open file and return the lines
def GetLines(filepath):
    file = open(filepath, 'r')
    lines = file.readlines()
    file.close()
    return lines

#Create an empty array of None and return it
def AllocateEmpty(width, height, adjust):
    arr = [None] * (height + adjust)
    for i in range(height + adjust):
        arr[i] = [None] * (width + adjust)

    return arr

#Parse each line of the file
def ParseLines(lines, filepath):

    #Get width and height, create an empty array to set
    width = len(lines[0]) - 1
    height = len(lines)
    print("Read in length: " + str(width))
    print("Lines: " + str(height))


    matrix = AllocateEmpty(width, height, 2)
    #Set valid characters, exit 1 if these are not the only ones present
    validChars = ['.', 'O', '\n']
    rowNum = 1

    #For each line
    for line in lines:
        #For each character
        for colNum in range(0, width):
            char = line[colNum]
            #Check validity of each character
            if char not in validChars:
                Error("Error: Invalid character detected in file.\nInvalid character was: '" + char + "'")
            #Set each cell
            matrix[rowNum][colNum + 1] = Cell(char, None)

        rowNum += 1

    print("Size of cell : " + str(sys.getsizeof(matrix[1][1])))
    return matrix

##############
# Write File #
##############

#Get the state of each cell so that we can return only characters, build a new array of characters from the objectarray
def ExtractCellState(matrix):
    width = len(matrix[0]) - 1
    height = len(matrix)  - 1
    writeMatrix = AllocateEmpty(width - 1, height - 1, 0)

    for row in range(1, height):
        for col in range(1, width):
            writeMatrix[row - 1][col - 1] = matrix[row][col].state #Extract the state and write it to a smaller matrix without border regions

    return writeMatrix

#Write the matrix to file, separated by newlines
def WriteMatrix(matrix, outputPath):
    writeMatrix = ExtractCellState(matrix)

    with open(outputPath, 'w') as file:
        for line in writeMatrix:
            file.write("".join(line) + "\n")
    file.close()
    return WriteMatrix

#################
# Simulate Wrap #
#################

#Acheived via creating memory references in the outer 1 cell edges of the array
#This way they never need handling as their referenced counterpart is updated inside the borders

#Set references in memory at each corner to their counterpart
def SetCorners(matrix, height, width):
    #print("Position : " + str(height + 1) + ", " + str(width))
    matrix[0][0] = matrix[height - 1][width - 1] #Get lower right, set upper left
    matrix[0][width] = matrix[height-1][1]
    matrix[height][0] = matrix[1][width-1]
    matrix[height][width] = matrix[1][1]

#Set the left and right columns between corners
def SetCols(matrix, height, width):
    for rowIndex in range(1, height):
        matrix[rowIndex][0] = matrix[rowIndex][width - 1]

    for rowIndex in range(1, height):
        matrix[rowIndex][width] = matrix[rowIndex][1]

#Set the top and bottom rows between corners, call SetCorners and call setCols.
#Border region is created on the matrix.
def ExpandBorders(matrix):
    width = len(matrix[0]) - 1
    height = len(matrix)  - 1#Get outer
    SetCorners(matrix, height, width)
    matrix[0][1:width] = matrix[height - 1][1:width]
    matrix[height][1:width] = matrix[1][1:width]
    SetCols(matrix, height, width)

#Automatically updates border regions as they are already pointers to the inner sections.
#OH WHAT A DAY! WHAT A LOVELY DAY - https://www.youtube.com/watch?v=2z2PKwLPrC0 - Leaving this in to show how well it started. This project was ultimately a nightmare of python inefficiencies for what I wanted to do

########################
# Splitting the Matrix #
########################

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


#############
# Debugging #
#############

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


##############################
# Parallel - Updating Matrix #
##############################

def JoinMatrices(matrix, matrixArray):
    row = 1

    #Update the first chunk of the array (at the top)
    for matriceRow in matrixArray[0][1:-1]:
        col = 1
        for cell in matriceRow[1:-1]:
            matrix[row][col].UpdateSelf(cell) #Use class function to update itself, so memory references stay intact rather than by assignment
            col += 1
        row +=1

    #Update every chunk in between the first and last
    for matrice in matrixArray[1:-1]:
        for matriceRow in matrice[1:-1]:
            col = 1
            for cell in matriceRow[1:-1]:
                matrix[row][col].UpdateSelf(cell)
                col += 1
            row +=1

    #Update the last chunk
    for matriceRow in matrixArray[-1][1:-1]:
        col = 1
        for cell in matriceRow[1:-1]:
            #print(matrix[row][col].state, end = "")
            matrix[row][col].UpdateSelf(cell)
            col += 1
        #print("\n")
        row +=1

############################
# Serial - Updating Matrix #
############################

#Set state to nextstate by class function, set nextstate to None
def SetNextIteration(matrix):
    height = len(matrix) - 1#Get outer indice
    width = len(matrix[0]) - 1

    for row in range(1, height):
        for col in range(1, width):
            #print(row, col)
            matrix[row][col].SetNextIteration()


########
# Main #
########

if __name__ == '__main__':
    startProgram = time.time()
    print("Project :: R11469438")

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

    neighborSteps = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

    ExpandBorders(matrix)

    if threads > 1:
        #Create a set of arguments for starmap
        data = []
        #Split the matrix into sections for each process
        matrixArray = SplitMatrix(matrix, threads)

        #Populate the arguments to starmap
        for index in range(threads):
            data.append([matrixArray[index], neighborSteps])

        #Create our pool
        process_pool = Pool(threads)
        for i in range(100):
            #Run starmap on ConvolveKinda with the given indice of arguments to each process
            output = process_pool.starmap(ConvolveKinda, data)
            #Update the matrix with the returned value when unblocked
            JoinMatrices(matrix, output)

        process_pool.close()
        process_pool.join()
    else:
        ExpandBorders(matrix)

        #Do it all here for speed, using already in place memory references.
        for i in range(100):
            ConvolveKinda(matrix, neighborSteps)
            SetNextIteration(matrix)

     #Beauty of it all being memory references


    WriteMatrix(matrix, outputPath)
    print("Total Execution Time: " + str(time.time() - startProgram))
