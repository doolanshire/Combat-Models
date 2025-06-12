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
import seaborn as sns

# The length of the time step will not alter the end result.
# Use only to determine the resolution of the graph.

timeStart = 0.0
timeEnd = 6.0
timeStep = 0.01

steps = int((timeEnd - timeStart) / timeStep)

# Initialise numpy arrays covering each step of the simulation.

blue = numpy.zeros(steps)
red = numpy.zeros(steps)
time = numpy.zeros(steps)

# Iwo Jima sample values: blue (US) = 54000; red (Japanese) = 21500;
# blueLethality = 0.0106; redLethality = 0.0544

blue[0] = 1000
red[0] = 500

blueLethality = 0.1
redLethality = 0.1

time[0] = timeStart

for i in range(steps -1):
    blue[i+1] = max(0, blue[i] - timeStep * (red[i] * redLethality))
    red[i+1] = max(0, red[i] - timeStep * (blue[i] * blueLethality))
    time[i+1] = time[i] + timeStep
    
# Remaining forces at the end of the simulation, for plot label purposes.
    
blueRemaining = int(blue[len(blue)-1])
redRemaining = int(red[len(red)-1])

# Plot code.
sns.set_theme(font='Times New Roman')
plot.figure()
plot.title("Lanchester Square Law", fontweight='bold', fontsize=16)
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
              
plot.show()