#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 2017

@author: Alvaro Radigales

A simple Python implementation of J.V. Chase's continuous fire equation.
Force strength for each time pulse of the simulation is stored in a NumPy
array, and later plotted using MatPlotLib. A separate NumPy array keeps
track of the equivalent ships remaining per side.

"""

import numpy

import matplotlib.pyplot as plot

from math import ceil

# The length of the time step will not alter the end result.
# Use only to determine the resolution of the graph.

timeStart = 0.0
timeEnd = 90.0
timeStep = 0.01

steps = int((timeEnd - timeStart) / timeStep)

# Initialise numpy arrays covering each step of the simulation.
# Two auxiliary arrays are used to store the equivalent number
# of ships left in each fleet.

blue = numpy.zeros(steps)
blueShips = numpy.zeros(steps)
red = numpy.zeros(steps)
redShips = numpy.zeros(steps)
time = numpy.zeros(steps)

blue[0] = 8
blueShips[0] = 8
red[0] = 7
redShips[0] = 7

blueLethality = 0.2
redLethality = 0.2

blueStaying = 12
redStaying = 12

time[0] = timeStart

for i in range(steps -1):
    blue[i+1] = max(0, blue[i] - (timeStep * (red[i] * redLethality)) / blueStaying)
    red[i+1] = max(0, red[i] - (timeStep * (blue[i] * blueLethality)) / redStaying)
    blueShips[i+1] = max(0, ceil(blue[i] - (timeStep * (red[i] * redLethality)) / blueStaying))
    redShips[i+1] = max(0, ceil(red[i] - (timeStep * (blue[i] * blueLethality)) / redStaying))
    time[i+1] = time[i] + timeStep
    
# Remaining forces at the end of the simulation, for plot label purposes.
    
blueRemaining = float("{0:.2f}".format(blue[len(blue)-1]))
redRemaining = float("{0:.2f}".format(red[len(red)-1]))
print(blue[len(blue)-1])

# Plot code.
    
plot.figure()
plot.gca().yaxis.grid(True)
plot.step(time, blue, '-b', where = 'post', label = 'Blue strength')
plot.step(time, blueShips, '-c', where = 'post', label = 'Blue ships')
plot.step(time, red, '-r', where = 'post', label = 'Red strength')
plot.step(time, redShips, '-m', where = 'post', label = 'Red ships')
plot.ylabel('Strength')
plot.xlabel('Time')
plot.legend()
plot.annotate(blueRemaining,
              xy=(timeEnd, blue[len(blue)-1]),
              xytext=(-15,10),
              textcoords='offset points')
plot.annotate(redRemaining,
              xy=(timeEnd, red[len(red)-1]),
              xytext=(-15,10),
              textcoords='offset points')
