# INSTRUCTIONS FOR TACTICAL AND STRATEGICAL EXERCISES

### CARRIED OUT ON TABLES OR BOARDS (January 1921)

 
A Python implementation of the *Instructions for Tactical and Strategical Exercises* as used for training in the Royal Navy in 1921. This is a work in progress.

## Objective

The aim of this project is implementing the fire and damage rules of the Tactical Exercise, in order to estimate attrition in historical battles.

Movement is not simulated directly – instead, the user introduces the firing intervals and targets for each ship group and the distances between them throughout a battle. The program then computes the exchange of fire accordingly.

Engagement information will eventually be stored in external CSV files so that different battles may be played with little effort.

## Done so far

#### Program files:

**guns\_and\_ships.py**: implements the _Gun_, _Ship_ and _Group_ classes and the necessary methods.

**plot.py**: a simple function to plot attrition over time.

#### Data files:

**capital\_ship\_guns.csv**: containing information on capital ship guns (16 in, 15 in I, 13.5 in V, and 12 in XI).

**light\_cruiser\_guns.csv**: containing information on light cruiser guns (7.5 in VI, and 6 in XII).

**destroyer\_guns.csv**: containing information on light cruiser guns (4.7 in I and 4 in V).

**secondary\_guns.csv**: containing information on secondary guns (6 in XII, 6 in VII, 5.5 in, 4 in IX, 4 in VII).

## To do
* Fix the *salvo size* parameter to represent the ratio of guns firing rather than an absolute number. The latter does
  not make a lot of sense when handling groups of different ship classes.
* Implement functions to read and parse ship data from external files.
* Design and implement engagement input files – essentially order of battle and fire events for each side.
* Add an option to define hit rates using an interpolation function rather than tabular data.
