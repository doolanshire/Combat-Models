# INSTRUCTIONS FOR TACTICAL AND STRATEGICAL EXERCISES

### CARRIED OUT ON TABLES OR BOARDS (January 1921)

 
A Python implementation of the *Instructions for Tactical and Strategical Exercises* as used for training in the Royal Navy in 1921. This is a work in progress.

## Objective

The aim of this project is implementing the fire and damage rules of the Tactical Exercise, in order to estimate attrition in historical battles.

Movement is not simulated directly – instead, the user introduces the firing intervals and targets for each ship group and the distances between them throughout a battle. The program then computes the exchange of fire accordingly.

All of the information for the model (gunnery data, ship specifications, orders of battle, engagement events etc.) is loaded from external, human-readable files.


#### Program files:

**battle_logic.py**: the main program file, containing all the logic of the model implementation.

**model_settings.cfg**: a configuration file determining the general behaviour of the model.


#### Data files and directories:

##### battle_data/

All engagement source files stored here. Battles are assigned a unique ID string (like *'cocos'* or *'coronel'*) and all their data files are placed in a directory bearing that name.

##### battle_data/[battle ID string]

* **[battle ID string].cfg**: a configuration file containing the general data of an engagement, such as its date, location, visibility, sea state, etc. Also determines the file paths of the fleet lists to use as source for the battle's ship roster.

* **side_a_groups.csv**: information on the groups of ships in side A, such as the group's name, the ships forming it, and whether it's a light division group or a main battle group. This latter distinction is relevant only for purposes of battle strength comparisons and is not actually needed by the model.

* **side_b_groups.csv**: see above.

* **side_a_evemts**: all battle events indicating side A's actions. Which groups shoot at which and at what range, when the firing starts and how long it lasts, and any modifiers to accuracy the user might want to add,

* **side_b_events**: see above.

##### fleets/

This directory contains the fleet lists used by the model, which hold the specifications of every ship used in every battle. All ships are unique and identified by their name, so there cannot be (for example) two HMS Orions in the same battle. If the user needs an exact copy of a given ship for whatever reason, they must add a new entry for it in the fleet lists and give it a unique name.

##### gun_data/

The gunnery tables for all guns described in the Instructions.

* **capital\_ship\_guns.csv**: containing information on capital ship guns (16 in, 15 in I, 13.5 in I and 12 in XI).

* **light\_cruiser\_guns.csv**: containing information on light cruiser guns (7.5 in VI, and 6 in XII).

* **destroyer\_guns.csv**: containing information on light cruiser guns (4.7 in I and 4 in V).

* **secondary\_guns.csv**: containing information on secondary guns (6 in XII, 6 in VII, 5.5 in, 4 in IX, 4 in VII).

A ***helper_functions*** directory contains some modules which are not necessary to run the model, but can be useful to prepare data for it.

##### reports/

When the relevant *model_settings.cfg* flags are set to *True*, the model will generate reports for each battle it simulates. These reports will be stored here, inside a sub-directory named after the battle's ID string.

## To do
* Make the model generate verbose per-minute reports of all combat actions, if only for debugging purposes.
