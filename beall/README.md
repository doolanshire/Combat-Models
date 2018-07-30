# Beall's Naval Combat Model

A Python implementation of the combat model created by Thomas Reagan Beall in 1990. This
is a Python 3.6 (and OOP-structured) version of Beall's original program, written in
Fortran77.

Refer to Beall's original thesis [here](https://calhoun.nps.edu/handle/10945/34842).

## Description

In Beall's combat model, each opposing side is composed of a number of "groups",
representing those naval units which fired or manoeuvred together in an engagement.

Each group has the following aggregate characteristics:

* **Staying power**: a function of the group's total displacement in tons. Defines how
much damage the group can withstand.
* **Continuous firepower**: a function of the weight of explosive ordnance the group
is able to fire continuously – that is, from its guns.
* **Pulse weapons**: weapons which deliver a certain amount of explosive power in
a discrete fashion, such as a torpedo or an aircraft bomb.

The battle is structured in a series of "fire events", in which groups fire their weapons
at other groups. In the case of continuous fire, the starting time and duration of the
barrage are specified. In the case of pulse weapons, the firing time and the time until
impact are specified.

The program then merges all events into a single timeline, iterates over it at one-minute
increments, and applies damage to the groups accordingly. The state of both forces at each
minute of the battle is printed out to the console, very closely preserving the format of
the original program's output files.

At the end of the file, after the class and function definitions, there are some examples
of battles with input values directly taken from Beall's thesis. Simply uncomment the
corresponding lines to run them.

## To do
At some point, and when I'm done with other projects, I might modify the program to load
battle data from external CSV files, in order to simplify playing around with the
simulation.

## Example output

                     CORONEL 1914                      

```BRITISH
Good Hope, Monmouth      SP: 3.21  | CF: 7.27  | PF: 0.0  
Glasgow                  SP: 1.23  | CF: 0.42  | PF: 0.0  

GERMAN
Scharnhorst, Gneisenau   SP: 3.3   | CF: 4.32  | PF: 0.0  
Leipzig, Dresden         SP: 2.23  | CF: 4.33  | PF: 0.0  


TP  - SPA    | CFA    | PFA    | SPB    | CFB    | PFB   
0   - 4.440  | 7.690  | 0.000  | 5.530  | 8.650  | 0.000 
1   - 4.319  | 7.416  | 0.000  | 5.530  | 8.650  | 0.000 
2   - 4.198  | 7.142  | 0.000  | 5.530  | 8.650  | 0.000 
3   - 4.077  | 6.868  | 0.000  | 5.530  | 8.650  | 0.000 
4   - 3.956  | 6.594  | 0.000  | 5.530  | 8.650  | 0.000 
5   - 3.835  | 6.320  | 0.000  | 5.530  | 8.650  | 0.000 
6   - 3.714  | 6.046  | 0.000  | 5.518  | 8.635  | 0.000 
7   - 3.594  | 5.773  | 0.000  | 5.506  | 8.619  | 0.000 
8   - 3.474  | 5.501  | 0.000  | 5.495  | 8.604  | 0.000 
9   - 3.354  | 5.230  | 0.000  | 5.483  | 8.588  | 0.000 
10  - 3.235  | 4.960  | 0.000  | 5.471  | 8.573  | 0.000 
11  - 3.116  | 4.691  | 0.000  | 5.459  | 8.558  | 0.000 
12  - 2.998  | 4.423  | 0.000  | 5.448  | 8.542  | 0.000 
13  - 2.880  | 4.156  | 0.000  | 5.436  | 8.527  | 0.000 
14  - 2.762  | 3.890  | 0.000  | 5.424  | 8.511  | 0.000 
15  - 2.645  | 3.625  | 0.000  | 5.412  | 8.496  | 0.000 
16  - 2.528  | 3.360  | 0.000  | 5.401  | 8.481  | 0.000 
17  - 2.412  | 3.097  | 0.000  | 5.389  | 8.465  | 0.000 
18  - 2.296  | 2.835  | 0.000  | 5.377  | 8.450  | 0.000 
19  - 2.129  | 2.556  | 0.000  | 5.365  | 8.434  | 0.000 
20  - 1.962  | 2.278  | 0.000  | 5.354  | 8.420  | 0.000 
21  - 1.848  | 2.019  | 0.000  | 5.354  | 8.420  | 0.000 
22  - 1.733  | 1.759  | 0.000  | 5.354  | 8.420  | 0.000 
23  - 1.619  | 1.500  | 0.000  | 5.354  | 8.420  | 0.000 
24  - 1.504  | 1.241  | 0.000  | 5.354  | 8.420  | 0.000 
25  - 1.390  | 0.981  | 0.000  | 5.354  | 8.420  | 0.000 
26  - 1.275  | 0.722  | 0.000  | 5.354  | 8.420  | 0.000 
27  - 1.161  | 0.463  | 0.000  | 5.354  | 8.420  | 0.000 
28  - 1.126  | 0.385  | 0.000  | 5.354  | 8.420  | 0.000 
29  - 1.126  | 0.385  | 0.000  | 5.354  | 8.420  | 0.000 

SUMMARY OF LOSSES (% LOST)
SA    | FCA   | FPA   | SB    | FCB   | FPB  
74.64 | 74.64 | 0.00  | 3.18  | 3.18  | 0.00 
```
