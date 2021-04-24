#########################################
# NAVAL WAR COLLEGE MANEUVER RULES 1922 #
#########################################

import os
import pandas as pd
import random


FIRE_EFFECT_TABLES_EDITION = "1922"


class Gun:
    """A naval gun. All parameters are loaded from external data files upon object creation. The only input needed is
    the gun's designation, which follows the format:

    [caliber]-in-[length]

    For example, '6-in-50' or '13.5-in-45'.

    The class attributes are:
    - designation: the gun's designation as explained above.
    - projectile_weight: the projectile weight in lbs.
    - muzzle_velocity: the gun's muzzle velocity in feet per second.
    - maximum_range: the gun's maximum range in thousands of yards.
    - hit_percentage: a dictionary containing Pandas dataframes. Holds to-hit chances at different ranges (at 2000-yard
    intervals) and for different spot types (top, kite or plane).
    - rate_of_fire: a Pandas dataframe with the expected rates of fire of any given gun when firing at different ranges
    (also at 2000-yard intervals).
    """

    def __init__(self, gun_designation):
        self.designation = gun_designation
        # Define the path for the gun's fire effect tables
        fire_effect_tables_path = "fire_effect_tables/{}/{}/".format(FIRE_EFFECT_TABLES_EDITION, gun_designation)

        # GENERAL DATA

        # Load the gun types dataframe.
        gun_types_path = "fire_effect_tables/{}/gun_types.csv".format(FIRE_EFFECT_TABLES_EDITION)
        general_data = pd.read_csv(gun_types_path, index_col="designation", na_values="--")
        # Fill out the gun's general data.
        self.projectile_weight = int(general_data["projectile_weight"][self.designation])
        self.muzzle_velocity = int(general_data["muzzle_velocity"][self.designation])
        self.maximum_range = int(general_data["maximum_range"][self.designation])

        # HIT PERCENTAGE

        # Define the paths for the hit percentage tables under different spot conditions.
        top_spot_path = "{}{}_percent_{}.csv".format(fire_effect_tables_path, self.designation, "top")
        kite_spot_path = "{}{}_percent_{}.csv".format(fire_effect_tables_path, self.designation, "kite")
        plane_spot_path = "{}{}_percent_{}.csv".format(fire_effect_tables_path, self.designation, "plane")
        # Create a hit percentage dictionary containing all the existing hit percentage tables.
        self.hit_percentage = {}
        if os.path.exists(top_spot_path):
            self.hit_percentage["top"] = pd.read_csv(top_spot_path, index_col='range', na_values="--", dtype=float)
        if os.path.exists(kite_spot_path):
            self.hit_percentage["kite"] = pd.read_csv(kite_spot_path, index_col='range', na_values="--", dtype=float)
        if os.path.exists(plane_spot_path):
            self.hit_percentage["plane"] = pd.read_csv(plane_spot_path, index_col='range', na_values="--", dtype=float)

        # RATE OF FIRE

        # Define the path for the rates of fire table.
        rates_of_fire_path = "fire_effect_tables/{}/rates_of_fire.csv".format(FIRE_EFFECT_TABLES_EDITION)

        # Create a rate of fire dataframe.
        self.rate_of_fire = pd.read_csv(rates_of_fire_path, index_col='range', na_values="--", dtype=float)

    def return_hit_percentage(self, target_size, target_range, spot_type):
        target_range = int(target_range)
        if target_range > self.maximum_range:
            return 0
        if not target_range % 2:
            return self.hit_percentage[spot_type][target_size][target_range]
        else:
            shorter_range = self.hit_percentage[spot_type][target_size][target_range - 1]
            longer_range = self.hit_percentage[spot_type][target_size][target_range + 1]
            return (shorter_range + longer_range) / 2

    def return_rate_of_fire(self, target_range, move_duration=1):
        if target_range > self.maximum_range:
            return 0
        if not target_range % 2:
            return self.rate_of_fire[self.designation][target_range] * move_duration
        else:
            shorter_range = self.rate_of_fire[self.designation][target_range - 1]
            longer_range = self.rate_of_fire[self.designation][target_range + 1]
            return ((shorter_range + longer_range) / 2) * move_duration

    def return_stochastic_hits(self, target_size, target_range, spot_type):
        hit_rate = self.return_hit_percentage(target_size, target_range, spot_type) / 100
        rate_of_fire = int(self.return_rate_of_fire(target_range))
        hits = sum([1 for _ in range(rate_of_fire) if random.random() < hit_rate])
        return hits


test_gun = Gun("6-in-50")
print(test_gun.return_hit_percentage("large", 16, "top"))
print(test_gun.return_rate_of_fire(16))
print(test_gun.return_stochastic_hits("large", 16, "top"))