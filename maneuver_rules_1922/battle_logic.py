#########################################
# NAVAL WAR COLLEGE MANEUVER RULES 1922 #
#########################################

import os
import pandas as pd
import random


FIRE_EFFECT_TABLES_EDITION = "1922"


class Gun:
    def __init__(self, gun_designation):
        self.designation = gun_designation
        # Define the path for the gun's fire effect tables
        fire_effect_tables_path = "fire_effect_tables/{}/{}/".format(FIRE_EFFECT_TABLES_EDITION, gun_designation)

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
        if not target_range % 2:
            return self.hit_percentage[spot_type][target_size][target_range]
        else:
            shorter_range = self.hit_percentage[spot_type][target_size][target_range - 1]
            longer_range = self.hit_percentage[spot_type][target_size][target_range + 1]
            return (shorter_range + longer_range) / 2

    def return_rate_of_fire(self, target_range, move_duration=1):
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


test_gun = Gun("6-in-53")
print(test_gun.return_hit_percentage("large", 16, "top"))
print(test_gun.return_rate_of_fire(16))
print(test_gun.return_stochastic_hits("large", 16, "top"))
