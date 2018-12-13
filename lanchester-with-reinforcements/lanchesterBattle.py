# coding: utf-8

# Lanchester Square Law with Reinforcements
# ================================================
# The code in this file models the Battle of
# Trafalgar as a series of three discrete separate
# actions, as proposed by W.P. Fox in the
# Proceeding of the 20th ICTCM.
# 
# Commented out immediately after is the battle
# modelled as a single exchange of fire, which
# the British fleet would be expected to lose.
#
# @author: Alvaro Radigales, 2018
# ================================================

from lanchesterLogic import *


# Define both sides
blue = Side('British Fleet', 13, 0.05)
red = Side('Combined Fleet', 3, 0.05)

# Set the replacement schedules for the three separate actions
blue_replacements = [(4, 14)]
red_replacements = [(4, 17), (19, 13)]

# Set the battle up and plot it
battle = Battle('Battle of Trafalgar', blue, red, 37, 0.01, blue_replacements, red_replacements)
battle.resolve()
battle.plot()

"""
# Trafalgar as a single exchange of fire

blue = Side('British Fleet', 27, 0.05)
red = Side('Combined Fleet', 33, 0.05)

# Set the replacement schedules for the three separate actions
blue_replacements = None
red_replacements = None

# Set the battle up and plot it
battle = Battle('Hypothetical scenario 2', blue, red, 24, 0.01, blue_replacements, red_replacements)
battle.resolve()
battle.plot()
"""
