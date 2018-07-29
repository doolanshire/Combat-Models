#Beall's Naval Combat Model
A Python implementation of the combat model created by Thomas Reagan Beall in 1983. This
is a Python 3.6 (and OOP-structured) version of Beall's original program, written in
Fortran77.
##Description
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

##To do
At some point, and when I'm done with other projects, I might modify the program to load
battle data from external CSV files, in order to simplify playing around with the
simulation.

###Dependencies
None. The Python standard library is all that is required.