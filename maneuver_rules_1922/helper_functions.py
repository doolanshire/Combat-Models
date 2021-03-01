"""
###########################################
## NAVAL WAR COLLEGE MANEUVER RULES 1922 ##
###########################################
A collection of helper functions and tools
to make the preparation and conduct of the
game easier
"""

import pandas as pd


def life_value(ship_class, t):
    """Return the life value of a ship in 14-inch hits.

    Arguments:
        - ship_class: takes the values below.
            * "BB post-Jutland"
            * "BB pre-Jutland"
            * "CC post-Jutland"
            * "OBB" ("old" battleship)
            * "BM" (monitor)
            * "CC pre-Jutland"
            * "OCC" ("old" battlecruiser)
            * "CA"
            * "OBM" ("old" monitor)
            * "OCA" ("old" armoured cruiser)
            * "CL"
            * "OCL" ("old" light cruiser)
            * "D" (destroyer or flotilla leader)
            * "A" (merchant)
            * "S" (submarine)

        - t: displacement in thousands of tons

        This last argument is named "t" (rather than a more descriptive name) to keep it
        consistent with the way the life formula is written in the Maneuver Rules.
    """

    # Read the external CSV file with the coefficient values
    life_coefficients = pd.read_csv("life_coefficients.csv", index_col=0, header=0)
    # Character of construction coefficient
    a = life_coefficients.loc[ship_class, "character_of_construction"]
    # Above-water tonnage coefficient
    b = life_coefficients.loc[ship_class, "above_water_tonnage"]
    # Q is unity for 14-inch shells
    q = 1
    # Square root of the ratio of total area to area of vitals
    sqrt_r = life_coefficients.loc[ship_class, "sqrt_area_to_vitals"]
    # Probability factor (Construction of Fire Effect Tables 1922, p. 31)
    p = (b * t ** (2/3)) / ((b * t ** (2/3)) + 3)
    # Life formula (Construction of Fire Effect Tables 1922, p. 31)
    life = a * (p * sqrt_r) * (b * t ** (1/3))
    return round(life, 2)


# Example 1: SMS Emden
print(life_value("CL", 3.6))
# Example 2: HMAS Sydney
print(life_value("CA", 5.5))
