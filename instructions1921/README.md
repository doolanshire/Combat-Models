# INSTRUCTIONS FOR TACTICAL AND STRATEGICAL EXERCISES

### CARRIED OUT ON TABLES OR BOARDS (January 1921)

 
A Python implementation of the *Instructions for Tactical and Strategical Exercises* as used for training in the Royal Navy in 1921. This is a work in progress.

## Objective

The aim of this project at least initially is to implement chiefly the firing and damage rules of the Tactical Exercise, in order to estimate attrition in historical battles.

Movement will not be implemented at first – instead, the analyst will introduce the firing intervals and targets for each ship and the distances between them throughout a battle, and the program will compute the attrition levels.

Engagement information will be saved in external CSV files so that different battles may be played effortlessly.

## Implemented so far

#### Program files:

**guns\_and\_ships.py**: class *Gun* partially implemented, containing the definition and associated methods for a given designation of naval gun. Data is loaded from an external CSV file containing naval gun parameters, which can be expanded or modified freely.

#### Data files:

**capital\_weapons.csv**: containing information on capital ship guns (16 in, 15 in I, 13.5 in V, and 12 in XI).

## To do
* Implement functions to read and parse the rest of the gun data, as well as the ship data.
* Add battle logic.
* Design and implement engagement input files.
