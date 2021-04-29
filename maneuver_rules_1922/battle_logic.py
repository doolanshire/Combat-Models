#########################################
# NAVAL WAR COLLEGE MANEUVER RULES 1922 #
#########################################

import os
import pandas as pd
import random


FIRE_EFFECT_TABLES_EDITION = "1930"


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

        self.caliber = float(self.designation.split("-")[0])

        # Load the gun types dataframe.
        gun_types_path = "fire_effect_tables/{}/gun_types.csv".format(FIRE_EFFECT_TABLES_EDITION)
        general_data = pd.read_csv(gun_types_path, index_col="designation", na_values="--")
        # Fill out the gun's general data.
        self.projectile_weight = int(general_data["projectile_weight"][self.designation])
        self.muzzle_velocity = int(general_data["muzzle_velocity"][self.designation])
        self.maximum_range = int(general_data["maximum_range"][self.designation])

        # HIT VALUE CONVERSION FACTORS

        # Define the paths for the hit value tables.
        penetrative_path = "fire_effect_tables/{}/hit_values_penetrative.csv".format(FIRE_EFFECT_TABLES_EDITION)
        non_penetrative_path = "fire_effect_tables/{}/hit_values_non_penetrative.csv".format(FIRE_EFFECT_TABLES_EDITION)
        # Load the data.
        self.penetrative_values = pd.read_csv(penetrative_path, index_col="caliber", dtype=float)
        self.non_penetrative_values = pd.read_csv(non_penetrative_path, index_col="caliber", dtype=float)

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
        """Returns the hit percentage of the gun for a given target size, range and spot type."""
        target_range = int(target_range)
        if target_range > self.maximum_range:
            return 0
        if not target_range % 2:
            return self.hit_percentage[spot_type][target_size][target_range] / 100
        else:
            shorter_range = self.hit_percentage[spot_type][target_size][target_range - 1]
            longer_range = self.hit_percentage[spot_type][target_size][target_range + 1]
            return (shorter_range + longer_range) / 2 / 100

    def return_rate_of_fire(self, target_range, move_duration=1):
        """Returns the rate of fire for the gun at a given range."""
        if target_range > self.maximum_range:
            return 0
        if not target_range % 2:
            return self.rate_of_fire[self.designation][target_range] / 3 * move_duration
        else:
            shorter_range = self.rate_of_fire[self.designation][target_range - 1]
            longer_range = self.rate_of_fire[self.designation][target_range + 1]
            return ((shorter_range + longer_range) / 2) / 3 * move_duration

    def return_hit_value(self, target_size, penetrative):
        if penetrative:
            if target_size == "submarine":
                return self.penetrative_values[target_size][self.caliber]
            else:
                return self.penetrative_values["large, intermediate, small, destroyer"][self.caliber]

        else:
            return self.non_penetrative_values[target_size][self.caliber]


class Ship:
    """A naval ship. All the data needed to instantiate a new Ship object can be found in the corresponding fleet list
    data files.

    Attributes:
        *General*
        - name (string): the name of the ship.
        - hull class (string): BB, CC, CA, CL, DD, etc. For a list of possible values check the file "life_coefficients"
        in the helper_functions directory.
        - size (string): large, intermediate, small, destroyer or submarine.
        - side (float): the side (belt) armour amidships, in inches.
        - deck (float): the deck armour amidships, in inches.

        *Primary armament*
        - primary_fire_effect_table (string): the fire effect table used by the primary armament (e.g. "6-in-50").
        - primary_total (int): the number of guns in the main battery.
        - primary_broadside (int): the number of guns the ship can fire broadside-on.
        - primary_bow (int): the number of guns the ship can fire at a target ahead.
        - primary_stern (int): the number of guns the ship can fire at a target astern.
        - primary_end_arc (int): the number of degrees from the bow or stern before the firing arc is considered to be
        broadside-on.

        *Secondary armament*
        As above, except with secondary_ as a prefix.

        *Torpedoes*
        - torpedoes_type (string): the type and caliber of the torpedoes carried by the ship, if any.
        - torpedoes_mount (string): whether the torpedo tubes are submerged (S) or deck-mounted (D).
        - torpedoes_total (int): total number of torpedo tubes.
        - torpedoes_side (int): number of torpedo tubes which can fire on either side.
        """

    def __init__(self, name, hull_class, size, life, side, deck, primary_fire_effect_table, primary_total,
                 primary_broadside, primary_bow, primary_stern, primary_end_arc, secondary_fire_effect_table,
                 secondary_total, secondary_broadside, secondary_bow, secondary_stern, secondary_end_arc,
                 torpedoes_type, torpedoes_mount, torpedoes_total, torpedoes_size):
        self.name = name
        self.hull_class = hull_class
        self.size = size
        self.life = life
        self.side = side
        self.deck = deck
        # Skip primary battery Gun creation if the ship has no significant primary armament.
        if primary_fire_effect_table != "NA":
            self.primary_armament = Gun(primary_fire_effect_table)
        else:
            self.secondary_armament = "NA"

        self.primary_total = primary_total
        self.primary_broadside = primary_broadside
        self.primary_bow = primary_bow
        self.primary_stern = primary_stern
        self.primary_end_arc = primary_end_arc
        # Skip secondary battery Gun creation if the ship has no significant secondary armament.
        if secondary_fire_effect_table != "NA":
            self.secondary_armament = Gun(secondary_fire_effect_table)
        else:
            self.secondary_armament = "NA"

        self.secondary_total = secondary_total
        self.secondary_broadside = secondary_broadside
        self.secondary_bow = secondary_bow
        self.secondary_stern = secondary_stern
        self.secondary_end_arc = secondary_end_arc
        # Torpedo tubes might be implemented in the future.
        self.torpedoes_type = torpedoes_type
        self.torpedoes_mount = torpedoes_mount
        self.torpedoes_total = torpedoes_total
        self.torpedoes_size = torpedoes_size

        # Remainder hits from previous salvo. Used in the stochastic model.
        self.remainder_hits = 0

    def calculate_primary_salvo_size(self, target_bearing):
        """Calculates the number of guns bearing on a target based on its bearing.

        Parameters:
            - target_bearing: the target bearing in degrees. Any input larger than 180 is appropriately converted.

        Returns: an integer representing the number of guns that can fire at a target at the input bearing.
        """
        if target_bearing > 180:
            target_bearing = 180 - (target_bearing % 180)
        # Check the arc within which the target lies.
        if target_bearing < self.primary_end_arc:
            salvo_size = self.primary_bow
        elif target_bearing > (180 - self.primary_end_arc):
            salvo_size = self.primary_stern
        else:
            salvo_size = self.primary_broadside

        return salvo_size

    def return_base_hits(self, target_size, target_range, target_bearing, spot_type, move_duration=1):
        """Returns the (deterministic) average number of hits expected per move, without any negative modifiers. This
        is calculated simply by multiplying the salvo size (number of guns bearing) by the rate of fire, and then by
        the percentage of hits expected for the target size, range and spot type.

        Parameters:
            - target_size (string): the size of the target (large, small, intermediate, destroyer or submarine).
            - target_range (int): the range to the target in thousands of yards beginning at 1.
            - target_bearing (int): the target bearing in degrees, with 90 meaning broadside on, 0 bow on and 180 stern.
            - spot_type (string): top, kite or plane spot. Bear in mind that from 1930 on the Naval War College's fire
            effect tables do not use kite spot.
            - move_duration (int): the duration of each move in minutes. Defaults to 1, because that is how this model
            simulates time increments. Change to 3 if you want to test whether the function returns values consistent
            with the ones in the Naval War College's fire effect tables.

        Returns: a float indicating the expected base number of hits.
        """

        salvo_size = self.calculate_primary_salvo_size(target_bearing)
        rate_of_fire = self.primary_armament.return_rate_of_fire(target_range, move_duration)
        base_to_hit = self.primary_armament.return_hit_percentage(target_size, target_range, spot_type)
        base_hits = salvo_size * rate_of_fire * base_to_hit

        return base_hits

    # This function is temporary and will be implemented somewhere else.
    def return_stochastic_hits(self, target_size, target_range, target_bearing, spot_type, move_duration=1):
        salvo_size = self.calculate_primary_salvo_size(target_bearing)
        rate_of_fire = self.primary_armament.return_rate_of_fire(target_range, move_duration)
        total_shots = (salvo_size * rate_of_fire) + self.remainder_hits
        self.remainder_hits = total_shots - int(total_shots)
        total_shots = int(total_shots)
        base_to_hit = self.primary_armament.return_hit_percentage(target_size, target_range, spot_type)
        hits = sum([1 for _ in range(total_shots) if random.random() < base_to_hit])

        return hits


class Group:
    def __init__(self, name, members, initial_speed, initial_course, initial_target):
        self.name = name
        self.members = members
        # Speed at the start and end of the move.
        self.initial_speed = initial_speed
        self.current_speed = None
        # Course at the start and end of the move.
        self.initial_course = initial_course
        self.current_course = None
        # Target at the start and end of the move.
        self.initial_target = initial_target
        self.current_target = None
        # Group life (nominal).
        self.life = sum(ship.life for ship in members)
        # Group life at the start and end of the move. Both are equal to the nominal group life upon creation.
        self.initial_life = self.current_life = self.life
        # Status.
        self.status = 1

    def add_ship(self, ship):
        self.members.append(ship)
        self.life += ship.life
        self.current_life += ship.hit_points
        self.status = self.current_life / self.life


test_gun = Gun("6-in-50")

sydney = Ship("Sydney", "CL", "small", 3.17, 3, 2, "6-in-50", 8, 4, 2, 2, 45, "NA", "NA", "NA", "NA", "NA", "NA",
              "B 21 in", "S", 2, 2)

print(sydney.return_base_hits("large", 16, 90, "top"))
results = []
for _ in range(10000):
    results.append(sydney.return_stochastic_hits("large", 16, 90, "top"))

print(sum(results)/len(results))

print(test_gun.return_hit_value("large", False))
