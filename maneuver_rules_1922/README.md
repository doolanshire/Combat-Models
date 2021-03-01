# MANEUVER RULES 1922

### TACTICAL LAYER


An automated Python implementation of the [Naval War College wargame](https://usnwc.edu/Research-and-Wargaming/Wargaming) in its 1922 iteration.


## Objectives

The aim of this project is to implement the fire and damage rules of the tactical layer of the game, in order to estimate attrition in historical battles.

Movement is not simulated directly – instead, the user introduces the firing intervals and targets for each ship group and the distances between them throughout a battle, as well as any other conditions affecting rate of fire, accuracy, etc. The program then computes the exchange of fire accordingly.

Engagement information will eventually be stored in external CSV files so that different battles may be played with little effort.

## Done so far

#### Program files:

* **helper_functions.py**: a series of utilities not strictly needed for the conduct of the game, but useful for its preparation - calculating ship life values, fighting strenghts, etc.

#### Data directories:

* **Fire effect tables**: containing CSV files with the fire effect tables for most naval guns or at least reasonably close equivalents.

## To do
Mostly everything
