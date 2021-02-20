# coding: utf-8

# Lanchester Square Law with Reinforcements
# ================================================
# An implementation of two classes ('Side' and
# 'Battle') to model Lanchester battles with
# reinforcements.
#
# @author: Alvaro Radigales, 2018
# ================================================

import numpy as np
import matplotlib.pyplot as plt


class Side:
    """One of two sides in a Lanchester battle.
    - name (string): for labelling purposes only, has no effect in the calculations.
    - strength (int): the strength in units of the side.
    - coefficient (fraction): Lanchester attrition coefficient (enemies killed per friendly per time increment)
    """

    def __init__(self, name, strength, coefficient):
        self.name = name
        self.strength = strength
        self.coefficient = coefficient

    def attack_power(self):
        """Return the side's attack power"""
        return self.strength * self.coefficient

    def damage(self, amount):
        """Inflict 'amount' number of casualties to the side"""
        self.strength -= min(amount, self.strength)


class Battle:
    """A Lanchester battle between two fighting sides.
    - name (string): for labelling purposes only, has no effect in the calculations.
    - blue (side): the side operating as 'blue' in the battle.
    - red (side): the side operating as 'red' in the battle.
    - duration: how many time increments will be simulated.
    – precision (fraction): battle resolution precision. 0.5 means two data points per time increment, 1 means one, etc.
    """

    def __init__(self, name, blue, red, duration, precision=-1, blue_replacements=None, red_replacements=None):
        self.name = name
        self.blue = blue
        self.red = red
        self.duration = duration
        self.precision = precision
        self.blue_replacements = blue_replacements
        self.red_replacements = red_replacements
        self.blue_plot = np.zeros(int(duration / precision))
        self.red_plot = np.zeros(int(duration / precision))
        self.time = np.zeros(int(duration / precision))

    def resolve(self):
        """Resolve the battle, storing strength values for each time pulse in a numpy array"""

        if self.blue_replacements:
            for replacements in self.blue_replacements:
                if isinstance(replacements, tuple):
                    self.blue_plot[int(replacements[0] / self.precision)] += replacements[1]
                    print(self.blue_plot[replacements[0]])

        if self.red_replacements:
            for replacements in self.red_replacements:
                if isinstance(replacements, tuple):
                    self.red_plot[int(replacements[0] / self.precision)] = replacements[1]

        self.blue_plot[0] = self.blue.strength
        self.red_plot[0] = self.red.strength
        self.time[0] = 0

        for i in range(int(self.duration / self.precision) - 1):
            self.blue_plot[i+1] += max(0, self.blue_plot[i] - self.precision * self.red_plot[i] * self.red.coefficient)
            self.red_plot[i+1] += max(0, self.red_plot[i] - self.precision * self.blue_plot[i] * self.blue.coefficient)
            self.time[i+1] = self.time[i] + self.precision

    def plot(self):
        """Plot the battle results as a function of time"""

        fig, ax = plt.subplots()
        plt.title(self.name)

        blue = ax.plot(self.time, self.blue_plot, color='tab:blue')
        red = ax.plot(self.time, self.red_plot, color='tab:red')

        ax.set_ylabel('Strength')
        ax.set_xlabel('Time')
        plt.title(self.name)

        ax.set_aspect(0.55)

        ax.legend((blue[0], red[0]), (self.blue.name, self.red.name), loc=1)

        blue_left = int(self.blue_plot[-1])
        red_left = int(self.red_plot[-1])

        ax.annotate(blue_left, xy=(self.time[-1], self.blue_plot[-1]), xytext=(-10, 10), textcoords='offset points')
        ax.annotate(red_left, xy=(self.time[-1], self.red_plot[-1]), xytext=(-10, 10), textcoords='offset points')

        ax.grid(which='major', axis='y', linestyle=':', alpha=0.5, zorder=0)
        ax.grid(which='minor', axis='y', linestyle=':', alpha=0.25, zorder=0)

        plt.show()
