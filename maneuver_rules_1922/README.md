# MANEUVER RULES 1922

### TACTICAL LAYER


An automated Python implementation of the [Naval War College wargame](https://usnwc.edu/Research-and-Wargaming/Wargaming) in its 1922 iteration.


## Objectives

The aim of this project is to implement the fire and damage rules of the tactical layer of the game, in order to estimate attrition in historical battles.

Movement is not simulated directly – instead, the user introduces the firing intervals and targets for each ship group and the distances between them throughout a battle, as well as any other conditions affecting rate of fire, accuracy, etc. The program then computes the exchange of fire accordingly.

Engagement information will eventually be stored in external CSV files so that different battles may be played with little effort.

## Done so far

#### Program logic:

* The *Gun*, *Ship*, *Group* and *Side* classes and their methods are partially implemented.
* The program can calculate (through methods belonging to the *Gun* class) rates of fire and basic to-hit chances at different ranges.
* Rate of fire is corrected based on various firing circumstances, such as establishing range or shifting targets.

#### Data:

* **Fire effect tables** collected for the following guns:
    + 6-in/53
    + 6-in/50
    + 4-in/50
    + 4-in/45 (AA)
    
  These include the total fire effect for a three-minute move, rates of fire, hit percentages and armour penetration figures.

## To do
* Finish the methods that apply corrections to rates of fire.
* Implement the methods that apply corrections to to-hit chances.
* Write the parser functions responsible for loading battle data.
* Implement the *Battle* class and its methods to handle battle timeline creation etc.