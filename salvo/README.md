# Hughes' Salvo Combat Model
A Python implementation (with plotting functionality) of the Salvo Combat Model
developed by Captain Wayne P. Hughes Jr., USN (Retired).
## Description
Two naval forces fight using Anti-Ship Cruise Missiles (ASCMs) over discrete combat
phases. Each phase is composed by the following events in succession:
* **Firing**: both sides fire simultaneously, massing all their missiles into a single salvo.
* **Defence**: the opposing forces attempt to intercept incoming missiles.
* **Damage**: missiles which are not intercepted strike their targets and cause damage.
Damage is applied simultaneously to both sides. Each ship takes damage until taken out
of action, and any excess damage moves over to the next ship. Damaged ships have their
offensive and defensive firepower reduced proportionally.
## File versions
**DeterministicSalvo.py** allows for "leakers" – a percentage of missiles that always
bypasses defences, so that neither side can ever be impervious to damage.
**DeterministicSalvoNoLeakers.py** as the name implies does not allow for "leakers".
In this version, the simulation is programmed to check whether the battle can reach
a stalemate – a situation in which neither force is able to damage each other.
*** Dependencies
Numpy and MatPlotLib are required.