# INSTRUCTIONS FOR TACTICAL AND STRATEGICAL EXERCISES

### CARRIED OUT ON TABLES OR BOARDS (January 1921)

 
A Python implementation of the *Instructions for Tactical and Strategical Exercises* as used for training in the Royal Navy in 1921. This is a work in progress.

## Objective

The aim of this project at least initially is to implement chiefly the firing and damage rules of the Tactical Exercise, in order to estimate attrition in historical battles.

Movement will not be implemented at first – instead, the analyst will introduce the firing intervals and targets for each ship and the distances between them throughout a battle, and the program will compute the attrition levels.

Engagement information will be saved in external CSV files so that different battles may be played effortlessly.

## Implemented so far

#### Program files:

**guns\_and\_ships.py**: class *Gun* partially implemented, containing the definition and associated methods for a given designation of naval gun. Data is loaded from external CSV files containing naval gun parameters, which can be expanded or modified freely.

Class *Ship* partially implemented, containing the definition and associated methods for a given ship belonging to one of the classes defined in the 1921 war game. Staying power is calculated upon creation from the ship class and armament type. Ship parameters have to be manually input for now.


#### Data files:

**capital\_ship\_guns.csv**: containing information on capital ship guns (16 in, 15 in I, 13.5 in V, and 12 in XI).

**light\_cruiser\_guns.csv**: containing information on light cruiser guns (7.5 in VI, and 6 in XII).

**destroyer\_guns.csv**: containing information on light cruiser guns (4.7 in I and 4 in V).

**secondary\_guns.csv**: containing information on secondary guns (6 in XII, 6 in VII, 5.5 in, 4 in IX, 4 in VII).

## To do
* Implement a "ship" class as an armoured container of gun objects.
* Implement functions to read and parse ship data.
* Add battle logic.
* Design and implement engagement input files.
