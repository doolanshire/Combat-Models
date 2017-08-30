#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 2017

@author: Alvaro Radigales

A simple Python implementation of the Lanchester Square Law. Force
strength for each time pulse of the simulation is stored in a NumPy
array, and later plotted using MatPlotLib.

"""

import numpy

import matplotlib.pyplot as plot

# The length of the time step will not alter the end result.
# Use only to determine the resolution of the graph.

timeStart = 0.0
timeEnd = 5.0
timeStep = 0.01

steps = int((timeEnd - timeStart) / timeStep)

# Initialise numpy arrays covering each step of the simulation.

blue = numpy.zeros(steps)
red = numpy.zeros(steps)
time = numpy.zeros(steps)

# Iwo Jima sample values: blue (US) = 54000; red (Japanese) = 21500;
# blueLethality = 0.0106; redLethality = 0.0544

blue[0] = 42
red[0] = 30

blueLethality = 0.2
redLethality = 0.2

time[0] = timeStart

for i in range(steps -1):
    blue[i+1] = max(0, blue[i] - timeStep * (red[i] * redLethality))
    red[i+1] = max(0, red[i] - timeStep * (blue[i] * blueLethality))
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