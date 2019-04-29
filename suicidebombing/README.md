# Kress' Suicide Bombing Model (modified)

A simulated variation of the analytical model for suicide bombing postulated by Moshe Kress in 2005. The model is explained and commented thoroughly in _Combat Modelling_ by Alan Washburn and Moshe Kress (Springer 2009). The original paper by Kress can be found [here](https://core.ac.uk/download/pdf/36730577.pdf).

## Description

The program generates a rectangular arena of size _x * y_ and populates it with a variable number of non-overlapping circular targets distributed semi-randomly.

An explosion with an arbitrary number of fragments is then generated in the centre of the arena. The fragments travel radially in semi-random directions until they hit a target or exit the area.

The purpose of the model is to demonstrate the phenomenon known as _crowd blocking_: targets near the origin of the fragments act as cover for targets further away, decreasing the overall lethality of the fragments. As a consequence of crowd blocking, bombing attacks in areas above a certain population density can be less lethal than predicted.

## Comparison to the analytical model

The analytical model by Kress uses a circular arena and assumes the targets are distributed in concentric rings around the centre.

![Example of an arena as seen in Kress' paper](https://github.com/doolanshire/Combat-Models/blob/master/suicidebombing/kressfig.png)

This simulation assumes a rectangular arena instead, in which targets are placed freely. The user specifies:

* The arena size _(x, y)_.
* The radius of the circular targets.
* The minimum distance between targets.
* The number of targets to attempt to place.

The program then starts adding targets at semi-random coordinates within the arena bounds. If a target lands at an illegal position, such as on top of another or within the minimum distance specified, placement fails, and the program proceeds to attempt to place the next target.

The explosion is then simulated, with a number of fragments specified by the user travelling in semi-random radii from the centre. The simulation provides a graphical representation using _matplotlib_.

![Example of an arena as simulated in the program](https://github.com/doolanshire/Combat-Models/blob/master/suicidebombing/sample.png)

The program prints out:

* The targets it fails to place (those landing in illegal positions)
* The percentage of the arena's area covered by successfully-placed targets. A higher percentage means a more densely populated arena.
* The number of targets killed by fragments.
* The number of fragments that have resulted in _overkill_ – by hitting targets which had already been hit by previous fragments. Used as a measurement of the effect of crowd blocking.

## To do

* Create a function that runs the simulation repeatedly and plots the number of casualties as a function of crowd density.
* Offer the user more options in arena creation.
* Find a nicer way of placing targets.
