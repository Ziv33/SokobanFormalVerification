# SokobanFormalVerification
Sokoban, Japanese for “warehouse keeper”, is a transport puzzle created by Hiroyuki Imabayashi in 1980. The goal of the game is simple, the warehouse keeper must push the boxes to designated locations in the warehouse.
The warehouse is depicted as a grid with walls creating a labyrinth. The following are rules that must be respected:
* Warehouse keeper can only move horizontally or vertically in the grid, one cell at a time.
* Boxes can only be pushed, not pulled, into an empty space.
* Warehouse keeper and boxes cannot enter “wall” cells.
  
In this project, we use the XSB format to describe the board.

For the SMV files, the XSB is reflected by the following mapping:
```bash
mapping = {
    "@": "whKeeper",        # Warehouse keeper
    "+": "whKeeperOnGoal",  # Warehouse keeper on goal
    "$": "box",             # Box
    "*": "boxOnGoal",       # Box on goal
    "#": "wall",            # Wall
    ".": "goal",            # Goal
    "-": "floorSign"        # floorSign
}
```

We use Python in order to automate definition of given input boards into SMV models. These models contain both the model and
the temporal logic formula defining a win.

For that, we created two scripts for both building the SMV files for the given boards using
automation and running these SMV files - ```BuildNuXmv.py``` and ```RunNuXmv.py``` respectively.

## Authors
* Ziv Chaba
* Hila Cohen

Questions can be directed to zivchaba1000@gmail.com

## Installation
Installation can be done in two ways:
* Clone the repository.
* Download specifically ```BuildNuXmv.py``` and ```RunNuXmv.py```.

In any case, you need to locate the two Python files in the same directory with ```nuXmv.exe```, and rootDir directory.

Inside the rootDir directory, you need to have three directories - ```part2XSBDir/```, ```part3XSBDir/``` and ```part4XSBDir/```, in which the XSB Sokoban boards files should be.

In addition, you need to have the python3 libraries- ```os```, ```subprocess```, ```time```, ```re``` and ```itertools```.

It is highly recommended to run ```RunNuXmv.py``` through PyCharm.

You can run the program by:
```bash
python3 RunNuXmv.py
```

All other directories should be generated automatically, as well as the summary file for each part, which can be found in the output directory for each part.



   
