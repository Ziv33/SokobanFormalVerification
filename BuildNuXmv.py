# Build the nuXmv files according to the given XSB format Sokoban boards.

# Import Libraries:
from itertools import combinations

# In our models, the XSB symbols cannot be used directly as some of them are saved symbols in SMV.
# Therefore, we will now define a key-value mapping between the XSB symbols to their SMV symbols.
mapping = {
    "@": "whKeeper",        # Warehouse keeper
    "+": "whKeeperOnGoal",  # Warehouse keeper on goal
    "$": "box",             # Box
    "*": "boxOnGoal",       # Box on goal
    "#": "wall",            # Wall
    ".": "goal",            # Goal
    "-": "floorSign"        # floorSign
}

class BuildNuXmv:
    def __init__(self, pathBoard = None, board = None, isIterative = 0):
        if board is not None:
            self.board = board
        else:
            self.board = self.boardTextTo2DList(pathBoard)
        self.whLocX = -1                # Warehouse keeper location on X axis
        self.whLocY = -1                # Warehouse keeper location on Y axis
        self.n = -1                     # Board's number of raws
        self.m = -1                     # Board's number of columns
        self.text = ''                  # The text of the output nuXmv file
        self.isIterative = isIterative  # Solve iteratively (for part 4)
        self.allGoalsLoc = None         # List of all goals' locations (for part 4)
        # Number of all empty original goals in the board (for part 4)
        self.numOriginalGoals = -1
        self.numCurrentGoals = -1       # Number of all current empty goals in the board - Initialization (for part 4)


    # Read the text XSB format Sokoban board, and turn it to a 2D list board:
    def boardTextTo2DList(self, path):
        board = []
        with open(path, 'r') as file:
            for line in file.readlines():
                if line[-1] == "\n":  # Ignore new line symbol
                    line = line[:-1]
                row = list(line)
                board.append(row)
        return board

    def getWhkeeperLoc(self):
        for i, rows in enumerate(self.board):
            for j, col in enumerate(rows):
                if col == '@' or col == '+':
                    return (i, j)
        return (-1, -1)


    # Get a list of coordinates of all goals (contains all  types - whKeeperOnGoal, boxOnGoal, goal):
    def getAllGoalsLocations(self):
        goalsCoordinates = []
        for i, rows in enumerate(self.board):
            for j, col in enumerate(rows):
                if col in ('.', '*', '+'):
                    goalsCoordinates.append((i,j))
        return goalsCoordinates




    # Write the complete text to the nuXmv file:
    def GenerateNuXmvFile(self, path):
        self.text += 'MODULE main\n'
        self.whLocY, self.whLocX = self.getWhkeeperLoc()
        # List of coordinates of all goals(contains all types - whKeeperOnGoal, boxOnGoal, goal):
        self.allGoalsLoc = self.getAllGoalsLocations()
        self.numOriginalGoals = sum(row.count('.') for row in self.board) + sum(row.count('+') for row in self.board)
        self.numCurrentGoals = self.numOriginalGoals  # Number of all current empty goals in the board
        self.n, self.m = len(self.board), len(self.board[0])
        self.defineSection()
        self.varSection()
        self.assignSection()
        if self.isIterative:
            self.text += '\nLTLSPEC !F(numCurrentGoals < numOriginalGoals)'
        else:
            self.text += '\nLTLSPEC !F(win)'
        with open(path, 'w') as f:
            f.write(self.text)

    # Add the DEFINE section to the SMV file:
    def defineSection(self):
        self.text += f'\nDEFINE'\
                        f'\n\tn := {self.n}; m := {self.m};'  # Board's given size
        if self.isIterative:
            self.text += f'\n\tnumOriginalGoals := {self.numOriginalGoals};'  # Board's number of all empty original goals in the board
        self.text += f'\n\twin :='                            # Win case
        for i in range(self.n):
            for j in range(self.m):
                self.text += f' (board[{i}][{j}] != box)'
                if (i == self.n - 1) & (j == self.m - 1):
                    self.text += ';\n'
                else:
                    self.text += f' &'



    # Add the VAR section to the SMV file:
    def varSection(self):
        self.text += f'\nVAR\n\tmove: {{start, l, u, r, d}};\n\tlOption: boolean;\n\tuOption: boolean;\n\trOption: boolean;\n\tdOption: boolean;'
        self.text += '\n\twhLocX: {'  # All the options for the warehouse keeper location on X axis
        for i in range(self.m):
            if i != 0:
                self.text += f', {i}'
            else:
                self.text += f'{i}'
        self.text += '};'
        self.text += '\n\twhLocY: {'  # All the options for the warehouse keeper location on X axis
        for i in range(self.n):
            if i != 0:
                self.text += f', {i}'
            else:
                self.text += f'{i}'
        self.text += '};'

        self.text += '\n\tnumCurrentGoals: {'  # Number of all current empty goals in the board
        for i in range(self.n * self.m + 1):
            if i != 0:
                self.text += f', {i}'
            else:
                self.text += f'{i}'
        self.text += '};'

        self.text += f'\n\tboard: array 0..{self.n - 1} of array 0..{self.m - 1} of {{whKeeper, whKeeperOnGoal, box, boxOnGoal, wall, goal, floorSign}};\n'

    # Add the ASSIGN section to the SMV file:
    def assignSection(self):
        self.text += f'\nASSIGN'

        # INIT
        for i in range(self.n):
            for j in range(self.m):
                self.text += f'\n\tinit(board[{i}][{j}]) := {mapping.get(self.board[i][j])};'  # Init the bard 2D array
        self.text += '\n'

        self.text += f'\n\tinit(move) := start;\n\tinit(whLocX) := {self.whLocX};\n\tinit(whLocY) := {self.whLocY};\n'
        self.text += f'\n\tinit(numCurrentGoals) := {self.numOriginalGoals};\n'


        self.text += f'\n\tinit(lOption) := '
        if self.whLocX <= 1:
            self.text += 'FALSE;'
        elif self.whLocX == 2:
            self.text += f'board[{self.whLocY}][{self.whLocX - 1}] = floorSign | board[{self.whLocY}][{self.whLocX - 1}] = goal;'
        elif self.whLocX >= 3:
            self.text += f'(board[{self.whLocY}][{self.whLocX - 1}] = floorSign) | (board[{self.whLocY}][{self.whLocX - 1}] = goal) | (board[{self.whLocY}][{self.whLocX - 1}] = boxOnGoal & board[{self.whLocY}][{self.whLocX - 2}] = floorSign) | (board[{self.whLocY}][{self.whLocX - 1}] = boxOnGoal & board[{self.whLocY}][{self.whLocX - 2}] = goal) | (board[{self.whLocY}][{self.whLocX - 1}] = box & board[{self.whLocY}][{self.whLocX - 2}] = floorSign) | (board[{self.whLocY}][{self.whLocX - 1}] = box & board[{self.whLocY}][{self.whLocX - 2}] = goal);'

        self.text += f'\n\tinit(uOption) := '  # Init the up option - boolean flag for when we can theoretically move up
        if self.whLocY <= 1:
            self.text += 'FALSE;'
        elif self.whLocY == 2:
            self.text += f'board[{self.whLocY - 1}][{self.whLocX}] = floorSign | board[{self.whLocY - 1}][{self.whLocX}] = goal;'
        elif self.whLocY >= 3:
            self.text += f'(board[{self.whLocY - 1}][{self.whLocX}] = floorSign) | (board[{self.whLocY - 1}][{self.whLocX}] = goal) | (board[{self.whLocY - 1}][{self.whLocX}] = boxOnGoal & board[{self.whLocY - 2}][{self.whLocX}] = floorSign) | (board[{self.whLocY - 1}][{self.whLocX}] = boxOnGoal & board[{self.whLocY - 2}][{self.whLocX}] = goal) | (board[{self.whLocY - 1}][{self.whLocX}] = box & board[{self.whLocY - 2}][{self.whLocX}] = floorSign) | (board[{self.whLocY - 1}][{self.whLocX}] = box & board[{self.whLocY - 2}][{self.whLocX}] = goal);'

        self.text += f'\n\tinit(rOption) := '
        if self.whLocX >= self.m - 2:
            self.text += 'FALSE;'
        elif self.whLocX == self.m - 3:
            self.text += f'board[{self.whLocY}][{self.whLocX + 1}] = floorSign | board[{self.whLocY}][{self.whLocX + 1}] = goal;'
        elif self.whLocX <= self.m - 4:
            self.text += f'(board[{self.whLocY}][{self.whLocX + 1}] = floorSign) | (board[{self.whLocY}][{self.whLocX + 1}] = goal) | (board[{self.whLocY}][{self.whLocX + 1}] = boxOnGoal & board[{self.whLocY}][{self.whLocX + 2}] = floorSign) | (board[{self.whLocY}][{self.whLocX + 1}] = boxOnGoal & board[{self.whLocY}][{self.whLocX + 2}] = goal) | (board[{self.whLocY}][{self.whLocX + 1}] = box & board[{self.whLocY}][{self.whLocX + 2}] = floorSign) | (board[{self.whLocY}][{self.whLocX + 1}] = box & board[{self.whLocY}][{self.whLocX + 2}] = goal);'


        self.text += f'\n\tinit(dOption) := '
        if self.whLocY >= self.n - 2:
            self.text += 'FALSE;'
        elif self.whLocY == self.n - 3:
            self.text += f'board[{self.whLocY + 1}][{self.whLocX}] = floorSign | board[{self.whLocY + 1}][{self.whLocX}] = goal;'
        elif self.whLocY <= self.n - 4:
            self.text += f'(board[{self.whLocY + 1}][{self.whLocX}] = floorSign) | (board[{self.whLocY + 1}][{self.whLocX}] = goal) | (board[{self.whLocY + 1}][{self.whLocX}] = boxOnGoal & board[{self.whLocY + 2}][{self.whLocX}] = floorSign) | (board[{self.whLocY + 1}][{self.whLocX}] = boxOnGoal & board[{self.whLocY + 2}][{self.whLocX}] = goal) | (board[{self.whLocY + 1}][{self.whLocX}] = box & board[{self.whLocY + 2}][{self.whLocX}] = floorSign) | (board[{self.whLocY + 1}][{self.whLocX}] = box & board[{self.whLocY + 2}][{self.whLocX}] = goal);'


        # NEXT
        self.text += f'\n\tnext(lOption) := case'
        self.text += f'\n\t\t(whLocX <= 1) : FALSE;'
        self.text += f'\n\t\t(whLocX = 2) : board[whLocY][self.whLocX - 1] = floorSign | board[whLocY][whLocX - 1] = goal;'
        self.text += f'\n\t\t(whLocX >= 3) : (board[whLocY][whLocX - 1] = floorSign) | (board[whLocY][whLocX - 1] = goal) | (board[whLocY][whLocX - 1] = boxOnGoal & board[whLocY][whLocX - 2] = floorSign) | (board[whLocY][whLocX - 1] = boxOnGoal & board[whLocY][whLocX - 2] = goal) | (board[whLocY][whLocX - 1] = box & board[whLocY][whLocX - 2] = floorSign) | (board[whLocY][whLocX - 1] = box & board[whLocY][whLocX - 2] = goal);'
        self.text += f'\n\t\tTRUE : FALSE;\n\tesac;\n'

        self.text += f'\n\tnext(uOption) := case'
        self.text += f'\n\t\t(whLocY <= 1) : FALSE;'
        self.text += f'\n\t\t(whLocY = 2) : board[whLocY - 1][whLocX] = floorSign | board[whLocY - 1][self.whLocX] = goal;'
        self.text += f'\n\t\t(whLocY >= 3) : (board[whLocY - 1][whLocX] = floorSign) | (board[whLocY - 1][whLocX] = goal) | (board[whLocY - 1][whLocX] = boxOnGoal & board[whLocY - 2][whLocX] = floorSign) | (board[whLocY - 1][whLocX] = boxOnGoal & board[whLocY - 2][whLocX] = goal) | (board[whLocY - 1][whLocX] = box & board[whLocY - 2][whLocX] = floorSign) | (board[whLocY - 1][whLocX] = box & board[whLocY - 2][whLocX] = goal);'
        self.text += f'\n\t\tTRUE : FALSE;\n\tesac;\n'

        self.text += f'\n\tnext(rOption) := case'
        self.text += f'\n\t\t(whLocX >= m - 2) : FALSE;'
        self.text += f'\n\t\t(whLocX = m - 3) : board[whLocY][whLocX + 1] = floorSign | board[whLocY][whLocX + 1] = goal;'
        self.text += f'\n\t\t(whLocX <= m - 4) : (board[whLocY][whLocX + 1] = floorSign) | (board[whLocY][whLocX + 1] = goal) | (board[whLocY][whLocX + 1] = boxOnGoal & board[whLocY][whLocX + 2] = floorSign) | (board[whLocY][whLocX + 1] = boxOnGoal & board[whLocY][whLocX + 2] = goal) | (board[whLocY][whLocX + 1] = box & board[whLocY][whLocX + 2] = floorSign) | (board[whLocY][whLocX + 1] = box & board[whLocY][whLocX + 2] = goal);'
        self.text += f'\n\t\tTRUE : FALSE;\n\tesac;\n'

        self.text += f'\n\tnext(dOption) := case'
        self.text += f'\n\t\t(whLocY >= n - 2) : FALSE;'
        self.text += f'\n\t\t(whLocY = n - 3) : board[whLocY + 1][whLocX] = floorSign | board[whLocY + 1][whLocX] = goal;'
        self.text += f'\n\t\t(whLocY <= n - 4) : (board[whLocY + 1][whLocX] = floorSign) | (board[whLocY + 1][whLocX] = goal) | (board[whLocY + 1][whLocX] = boxOnGoal & board[whLocY + 2][whLocX] = floorSign) | (board[whLocY + 1][whLocX] = boxOnGoal & board[whLocY + 2][whLocX] = goal) | (board[whLocY + 1][whLocX] = box & board[whLocY + 2][whLocX] = floorSign) | (board[whLocY + 1][whLocX] = box & board[whLocY + 2][whLocX] = goal);'
        self.text += f'\n\t\tTRUE : FALSE;\n\tesac;\n'

        self.text += f'\n\tnext(whLocX) := case\n\t\t(next(move) = r) & (whLocX < m - 1) : whLocX + 1;\n\t\t(next(move) = l) & (whLocX > 0) : whLocX - 1;\n\t\tTRUE : whLocX;\n\tesac;\n'

        self.text += f'\n\tnext(whLocY) := case\n\t\t(next(move) = d) & (whLocY < n - 1) : whLocY + 1;\n\t\t(next(move) = u) & (whLocY > 0) : whLocY - 1;\n\t\tTRUE : whLocY;\n\tesac;\n'

        # We create all possible options of conditions to decide where to move for next(move):
        anotherMoveOption = f'& '
        newMoveOption = f'\n\t\t'
        self.text += f'\n\tnext(move) := case'
        allMoves = ['l', 'u', 'r', 'd']
        for i in range(4, 0, -1):
            for moveGroup in list(combinations(allMoves, i)):
                moveOptionDetected = False
                if 'l' in moveGroup:
                    self.text += f'\n\t\tnext(lOption) '
                    moveOptionDetected = True

                if 'u' in moveGroup:
                    if moveOptionDetected:
                        self.text += anotherMoveOption
                    else:
                        self.text += newMoveOption
                    moveOptionDetected = True
                    self.text += f'next(uOption) '

                if 'r' in moveGroup:
                    if moveOptionDetected:
                        self.text += anotherMoveOption
                    else:
                        self.text += newMoveOption
                    moveOptionDetected = True
                    self.text += f'next(rOption) '

                if 'd' in moveGroup:
                    if moveOptionDetected:
                        self.text += anotherMoveOption
                    else:
                        self.text += newMoveOption
                    moveOptionDetected = True
                    self.text += f'next(dOption) '

                self.text += ': {' + ', '.join(moveGroup) + '};'

        self.text += f'\n\t\tTRUE : start;\n\tesac;\n'


        # next(board)
        for i in range(self.n):
            for j in range(self.m):
                self.text += f'\n\tnext(board[{i}][{j}]) := case' \
                                f'\n\t\t(whLocY = {i}) & (whLocX = {j}) & (board[{i}][{j}] = whKeeper) & (next(move) = l | next(move) = u | next(move) = r | next(move) = d) : floorSign;' \
                                f'\n\t\t(whLocY = {i}) & (whLocX = {j}) & (board[{i}][{j}] = whKeeperOnGoal) & (next(move) = l | next(move) = u | next(move) = r | next(move) = d) : goal;'
                if i > 0:
                    self.text += f'\n\t\t(whLocY = {i - 1}) & (whLocX = {j}) & ((board[{i}][{j}] = floorSign) | (board[{i}][{j}] = box)) & (next(move) = d) : whKeeper;' \
                                    f'\n\t\t(whLocY = {i - 1}) & (whLocX = {j}) & ((board[{i}][{j}] = goal) | (board[{i}][{j}] = boxOnGoal)) & (next(move) = d) : whKeeperOnGoal;'
                if i > 1:
                    self.text += f'\n\t\t(whLocY = {i - 2}) & (whLocX = {j}) & ((board[{i - 1}][{j}] = boxOnGoal) | (board[{i - 1}][{j}] = box)) & (board[{i}][{j}] = floorSign) & (next(move) = d) : box;' \
                                    f'\n\t\t(whLocY = {i - 2}) & (whLocX = {j}) & ((board[{i - 1}][{j}] = boxOnGoal) | (board[{i - 1}][{j}] = box)) & (board[{i}][{j}]= goal) & (next(move) = d) : boxOnGoal;'
                if i < self.n - 1:
                    self.text += f'\n\t\t(whLocY = {i + 1}) & (whLocX = {j}) & ((board[{i}][{j}] = floorSign) | (board[{i}][{j}] = box)) & (next(move) = u) : whKeeper;' \
                                    f'\n\t\t(whLocY = {i + 1}) & (whLocX = {j}) & ((board[{i}][{j}] = goal) | (board[{i}][{j}] = boxOnGoal)) & (next(move) = u) : whKeeperOnGoal;'
                if i < self.n - 2:
                    self.text += f'\n\t\t(whLocY = {i + 2}) & (whLocX = {j}) & ((board[{i + 1}][{j}] = boxOnGoal) | (board[{i + 1}][{j}] = box)) & (board[{i}][{j}] = floorSign) & (next(move) = u) : box;' \
                                    f'\n\t\t(whLocY = {i + 2}) & (whLocX = {j}) & ((board[{i + 1}][{j}] = boxOnGoal) | (board[{i + 1}][{j}] = box)) & (board[{i}][{j}] = goal) & (next(move) = u) : boxOnGoal;'
                if j > 0:
                    self.text += f'\n\t\t(whLocY = {i}) & (whLocX = {j - 1}) & ((board[{i}][{j}] = floorSign) | (board[{i}][{j}] = box)) & (next(move) = r) : whKeeper;' \
                                    f'\n\t\t(whLocY = {i}) & (whLocX = {j - 1}) & ((board[{i}][{j}] = goal) | (board[{i}][{j}] = boxOnGoal)) & (next(move) = r) : whKeeperOnGoal;'
                if j > 1:
                    self.text += f'\n\t\t(whLocY = {i}) & (whLocX = {j - 2}) & ((board[{i}][{j - 1}] = boxOnGoal) | (board[{i}][{j - 1}] = box)) & (board[{i}][{j}] = floorSign) & (next(move) = r) : box;' \
                                    f'\n\t\t(whLocY = {i}) & (whLocX = {j - 2}) & ((board[{i}][{j - 1}] = boxOnGoal) | (board[{i}][{j - 1}] = box)) & (board[{i}][{j}] = goal) & (next(move) = r) : boxOnGoal;'
                if j < self.m - 1:
                    self.text += f'\n\t\t(whLocY = {i}) & (whLocX = {j + 1}) & ((board[{i}][{j}] = floorSign) | (board[{i}][{j}] = box)) & (next(move) = l) : whKeeper;' \
                                    f'\n\t\t(whLocY = {i}) & (whLocX = {j + 1}) & ((board[{i}][{j}] = goal) | (board[{i}][{j}] = boxOnGoal)) & (next(move) = l) : whKeeperOnGoal;'
                if j < self.m - 2:
                    self.text += f'\n\t\t(whLocY = {i}) & (whLocX = {j + 2}) & ((board[{i}][{j + 1}] = boxOnGoal) | (board[{i}][{j + 1}] = box)) & (board[{i}][{j}] = floorSign) & (next(move) = l) : box;' \
                                    f'\n\t\t(whLocY = {i}) & (whLocX = {j + 2}) & ((board[{i}][{j + 1}] = boxOnGoal) | (board[{i}][{j + 1}] = box)) & (board[{i}][{j}] = goal) & (next(move) = l) : boxOnGoal;'
                self.text += f'\n\t\tTRUE : board[{i}][{j}];\n\tesac;\n'

        if self.isIterative:  # next(numCurrentGoals)
            self.text += f'\n\tnext(numCurrentGoals) := case' \
                         f'{self.generateConditions(self.allGoalsLoc)}\n\tesac;\n'



    def generateConditions(self, LocationsList, target="boxOnGoal"):
        conditions = []
        n = len(LocationsList)

        # Generate conditions for all combinations from all to none
        for k in range(n, -1, -1):
            if k == 0:
                # Default case when none of the locations is boxOnGoal
                conditions.append(f'\n\t\tTRUE : numOriginalGoals;')
            else:
                for combo in combinations(LocationsList, k):
                    condition = ' & '.join([f'board[{i}][{j}] = {target}' for (i, j) in combo])
                    num_remaining = n - k
                    conditions.append(f'\n\t\t({condition}) : {num_remaining};')

        return ''.join(conditions)

