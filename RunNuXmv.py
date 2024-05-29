# Run the nuXmv models


# Import Libraries:
import os
import subprocess
import time
import re

# Import modules:
from BuildNuXmv import BuildNuXmv
from BuildNuXmv import mapping

# Part 2
def runNuXmvPart2(part2XSBDir, part2SMVDir, rootDir):

    for fileName in os.listdir(part2XSBDir):
        if fileName.endswith(".txt"):
            fileFullPath = os.path.join(part2XSBDir, fileName)
            writer = BuildNuXmv(fileFullPath)
            writer.GenerateNuXmvFile(part2SMVDir + "/" + fileName[:-4] + ".smv")


    # Create output directory if it doesn't exist
    outputDir = os.path.join(rootDir, "Part2Outputs")
    os.makedirs(outputDir, exist_ok=True)

    # Iterate over files in the directory
    for fileName in os.listdir(part2SMVDir):
        if fileName.endswith(".smv"):
            filePath = os.path.join(part2SMVDir, fileName)
            outputFilePath = os.path.join(outputDir, fileName[
                                                              :-4] + "Output.txt")  # Output file name based on input file name

            # Run nuxmv.exe command
            command = ["nuxmv.exe", filePath]
            try:
                with open(outputFilePath, "w") as outputFile:
                    subprocess.run(command, stdout=outputFile, stderr=subprocess.PIPE, check=True)
                print(f"Successfully ran nuxmv.exe on {fileName}")
            except subprocess.CalledProcessError as e:
                print(f"Error running nuxmv.exe on {fileName}: {e.stderr.decode()}")

    # Results' summary
    generateSummaryPart2(rootDir)

def generateSummaryPart2(directory):
        summaryFilePath = os.path.join(directory, "Part2Outputs", "summaryOutputs.txt")
        with open(summaryFilePath, "w") as summaryFile:
            summaryFile.write("***********************\n")  # Write header
            summaryFile.write("* PART 2 - Summary *\n")  # Write header
            summaryFile.write("***********************\n\n")  # Write header
            for filename in os.listdir(os.path.join(directory, "Part2Outputs")):
                if filename.endswith("Output.txt"):
                    outputFilePath = os.path.join(directory, "Part2Outputs", filename)
                    winnable, outputText = checkWinability(outputFilePath)
                    if winnable is None:
                        print(f"Unable to determine winnability for {filename}")
                    elif winnable:
                        summaryFile.write(
                            f"{filename[:-10]} is winnable. The winning solution (LURD Format): {extractWinningSolution(outputText)}.\n")
                    else:
                        summaryFile.write(f"{filename[:-10]} is not winnable.\n")
        print("Summary generation for Part 2 is completed.")

def checkWinability(outputFilePath):
    with open(outputFilePath, "r") as outputFile:
        outputText = outputFile.read()
        if "is false" in outputText:
            return True, outputText
        elif "is true" in outputText:
            return False, outputText
        else:
            return None, None

def extractWinningSolution(outputText):
    LURDWinMoves = ""
    lastMove = ""
    if (len(outputText.split("-- Loop starts here")[0].split("-> State: 1.2 ")) == 1):
        return "[EMPTY: ALREADY SOLVED]"
    states = outputText.split("-- Loop starts here")[0].split("-> State: 1.2 ")[1].split("-> State:")  # First state is always move = start (initialization value)
    for state in states:
        useLastMove = False
        lines = state.split("\n")
        for line in lines:
            if "move" in line:
                move = line.split("=")[1].strip().lower()
                LURDWinMoves += move
                lastMove = move
                useLastMove = True
                break
        if not useLastMove:
            LURDWinMoves += lastMove
        if "-- Loop starts here" in state:
            break
    if LURDWinMoves == "":
        return False
    return LURDWinMoves

# Part 3
# We assume we get only winnable (solvable) board. The way to win in LURD format is given in Part 2.
# Now we want to compare the performance of BDD and SAT Solver Engines, by measuring the run time of each winnable board
# On these solver engines.


def runNuXmvPart3(part3XSBDir, part3SMVDir, rootDir):

    for fileName in os.listdir(part3XSBDir):
        if fileName.endswith(".txt"):
            fileFullPath = os.path.join(part3XSBDir, fileName)
            writer = BuildNuXmv(fileFullPath)
            writer.GenerateNuXmvFile(part3SMVDir + "/" + fileName[:-4] + ".smv")


    # Create output directory if it doesn't exist
    outputDir = os.path.join(rootDir, "Part3Output")
    os.makedirs(outputDir, exist_ok=True)

    # Summary file for Part 3
    summaryFilePath = os.path.join(outputDir, "summaryOutputs.txt")
    with open(summaryFilePath, "w") as summaryFile:
        summaryFile.write("***********************\n")  # Write header
        summaryFile.write("* PART 3 - Summary *\n")  # Write header
        summaryFile.write("***********************\n\n")  # Write header

        # Iterate over the SMV in the directory of winnable boards:
        for fileName in os.listdir(part3SMVDir):
            if fileName.endswith(".smv"):
                filePath = os.path.join(part3SMVDir, fileName)
                # Write the run time of each Solver Engine:
                summaryFile.write(f'{fileName.split(".smv")[0]} is winnable with BDD Solver Engine in {BDDSolverEngine(filePath, outputDir, fileName)}, while with SAT Solver Engine it is winnable in {SATSolverEngine(filePath, outputDir, fileName)[0]}.\n')
    print("Summary generation for Part 3 is completed.")



def BDDSolverEngine(path, outputDir, fileName):
    start = time.time()

    # Run nuXmv in interactive mode
    process = subprocess.Popen(
        ["nuXmv", "-int", path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )

    # Send commands to nuXmv
    runBDD = "go\ncheck_ltlspec\nquit\n"
    stdout, _ = process.communicate(input=runBDD)

    # Current output file
    outputFilePath = os.path.join(outputDir, fileName[:-4] + "OutputBDD.txt")
    with open(outputFilePath, "w") as outputFile:
        outputFile.write(stdout)

    end = time.time()

    diffTime = end - start

    # Check if board winnable (solvable)
    if "is false" in stdout:
        LURDmove = extractWinningSolution(stdout)
        return str(diffTime) + " seconds, and the winning solution (LURD Format) is: " + LURDmove
    else:
        return "ERROR: THE GIVEN BOARD IS NOT WINNABLE."



def SATSolverEngine(path, outputDir, fileName):
    start = time.time()

    # Run nuXmv in interactive mode
    process = subprocess.Popen(
        ["nuXmv", "-int", path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        universal_newlines=True
    )

    # Send commands to nuXmv - we bounce the number of steps to be 100 since from last part we saw that the winning path
    # contains less than 100 moves, for all our given boards. This definition can change.
    runSAT = "go_bmc\ncheck_ltlspec_bmc -k 100\nquit\nquit\n"
    stdout, _ = process.communicate(input=runSAT)

    # Current output file
    outputFilePath = os.path.join(outputDir, fileName[:-4] + "OutputSAT.txt")
    with open(outputFilePath, "w") as outputFile:
        outputFile.write(stdout)

    end = time.time()
    diffTime = end - start

    # Check if board winnable (solvable)
    if "is false" in stdout:
        LURDmove = extractWinningSolution(stdout)
        return [str(diffTime) + " seconds, and the winning solution (LURD Format) is: " + LURDmove, str(diffTime), LURDmove]
    else:
        return "ERROR: THE GIVEN BOARD IS NOT WINNABLE."



# Part 4
# Now, we will break the problem into sub-problems by solving the boards iteratively.
# We will run loops on the numbers of remaining goals for each iteration, so that by the LTL specification we will check
# if we reduced the number of goals (so that they turned to be boxOnGoal) relating to previous iteration, and when we will
# reach to zero remaining box, we will stop.

def boardUpdate(output, rows, cols):
    # Search if not solvable
    if re.search('-- specification.*is true', output) or re.search('-- no counterexample found with bound 100', output):
        return None

    # Modify the board with all the last changes
    board = [[] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            finalChange = re.findall(f'board\\[{i}\\]\\[{j}\\] = ([a-za-zA-Z]+)', output)[-1]
            board[i].append(fromValToKey(mapping,finalChange))

    return board

def fromValToKey(d, value):
    return next((k for k, v in d.items() if v == value), None)

def runIterativeNuXmvPart4(part4XSBDir, part4SMVDir, rootDir):
    # Create output directory if it doesn't exist
    outputDir = os.path.join(rootDir, "Part4Output")
    os.makedirs(outputDir, exist_ok=True)

    # Summary file for Part 4
    summaryFilePath = os.path.join(outputDir, "summaryOutputs.txt")
    with open(summaryFilePath, "w") as summaryFile:
        summaryFile.write("***********************\n")  # Write header
        summaryFile.write("* PART 4 - Summary *\n")  # Write header
        summaryFile.write("***********************\n\n")  # Write header

    for fileName in os.listdir(part4XSBDir):
        if fileName.endswith(".txt"):
            totalRuntime = 0
            totalLURD = ''
            fileFullPath = os.path.join(part4XSBDir, fileName)
            writer = BuildNuXmv(pathBoard=fileFullPath, isIterative=1)
            tempBoard = writer.board.copy()

            numIteration = 0
            while any(('.' in row or '+' in row) for row in tempBoard):  # While there is empty goal
                numIteration += 1
                filePath = part4SMVDir + "/" + fileName[:-4] + f'Iteration{numIteration}' + ".smv"
                writer.GenerateNuXmvFile(filePath)
                start = time.time()

                # Run nuXmv in interactive mode
                process = subprocess.Popen(
                    ["nuXmv", "-int", filePath],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    universal_newlines=True
                )

                # Send commands to nuXmv - we bounce the number of steps to be 100 since from last part we saw that the winning path
                # contains less than 100 moves, for all our given boards. This definition can change.
                runSAT = "go_bmc\ncheck_ltlspec_bmc -k 100\nquit\nquit\n"
                stdout, _ = process.communicate(input=runSAT)

                end = time.time()
                diffTime = end - start
                LURDmove = extractWinningSolution(stdout)

                totalRuntime += diffTime
                totalLURD += LURDmove

                # Current iteration output file and adding to summary file
                outputFilePath = outputDir + "/" + fileName[:-4] + f'Iteration{numIteration}Output' + ".txt"
                with open(outputFilePath, "w") as outputFile:
                    outputFile.write(stdout)
                    outputFile.write(f'\nThe iteration time is {diffTime} seconds.')
                with open(summaryFilePath, "a") as summaryFile:
                    summaryFile.write(f'\nThe {fileName.split(".txt")[0]} run time in iteration number {numIteration} is {diffTime} seconds.')

                # Update the board for the next iteration:
                tempBoard = boardUpdate(stdout, len(writer.board), len(writer.board[0]))
                if tempBoard is None:
                    with open(summaryFilePath, "a") as summaryFile:
                        summaryFile.write(f'\nThe {fileName.split(".txt")[0]} is not solvable.')
                    break
                writer = BuildNuXmv(board=tempBoard, isIterative=1)
                tempBoard = writer.board.copy()

            with open(summaryFilePath, "a") as summaryFile:
                summaryFile.write(f'\nThe {fileName.split(".txt")[0]} total run time is {totalRuntime} seconds, the numbers of '
                             f'iterations for solving is {numIteration}, and the winning solution (LURD Format) is: {totalLURD[:-1]}.\n\n')

    print("Summary generation for Part 4 is completed.")

def main():
    # The user have to create these directories, and insert to the XSBDir-s the XSB Sokoban boards before running this program.
    rootDir = 'rootDir/'  # Root directory - in the same directory as the python files and nuXmv.exe file.

    # Part 2:
    part2XSBDir = "rootDir/part2XSBDir"  # The XSB format of given boards.
    part2SMVDir = "rootDir/part2SMVDir"  # The directory with all the SMV models that were generated.
    runNuXmvPart2(part2XSBDir, part2SMVDir, rootDir)

    # Part 3:
    part3XSBDir = "rootDir/part3XSBDir"  # The XSB format of given winnable (solvable) boards.
    part3SMVDir = "rootDir/part3SMVDir"  # The directory with all the SMV models that were generated.
    runNuXmvPart3(part3XSBDir, part3SMVDir, rootDir)

    # Part 4:
    part4XSBDir = "rootDir/part4XSBDir"  # The XSB format of given winnable (solvable) boards.
    part4SMVDir = "rootDir/part4SMVDir"  # The directory with all the SMV models that were generated.
    runIterativeNuXmvPart4(part4XSBDir, part4SMVDir, rootDir)



# Main
if __name__ == '__main__':
    main()