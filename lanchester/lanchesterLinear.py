#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 2017

@author: Alvaro Radigales

A simple Python implementation of the Lanchester Linear Law. Force
strength for each time pulse of the simulation is stored in a NumPy
array, and later plotted using MatPlotLib.

"""

import numpy

import matplotlib.pyplot as plot

from math import ceil

# The length of the time step will not alter the end result.
# Use only to determine the resolution of the graph.

timeStart = 0.0
timeEnd = 10.0
timeStep = 0.01

steps = int((timeEnd - timeStart) / timeStep)

# Initialise numpy arrays covering each step of the simulation.

blue = numpy.zeros(steps)
red = numpy.zeros(steps)
time = numpy.zeros(steps)

# To remove the frontage constraint, change the frontage variable to
# the smaller remaining force, both in its declaration and in the loop.

blue[0] = 42
red[0] = 30
frontage = 5

blueLethality = 1
redLethality = 1

time[0] = timeStart

for i in range(steps -1):
    frontage = min(frontage, ceil(red[i]), ceil(blue[i]))
    blue[i+1] = max(0, blue[i] - timeStep * (frontage * redLethality))
    red[i+1] = max(0, red[i] - timeStep * (frontage * blueLethality))
    time[i+1] = time[i] + timeStep
    
# Remaining forces at the end of the simulation, for plot label purposes.
    
blueRemaining = int(blue[len(blue)-1])
redRemaining = int(red[len(red)-1])

# Plot code.
    
plot.figure()
plot.step(time, blue, '-b', where = 'post', label = 'Blue army')
plot.step(time, red, '-r', where = 'post', label = 'Red army')
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