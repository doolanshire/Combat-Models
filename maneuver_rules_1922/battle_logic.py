#########################################
# NAVAL WAR COLLEGE MANEUVER RULES 1922 #
#########################################

# import math
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

        # ARMOUR PENETRATION

        # Define the path for the side armor penetration ranges table.
        side_penetration_ranges_path = "{}{}_side_penetration_ranges.csv".format(fire_effect_tables_path,
                                                                                 self.designation)

        # Create a side penetration ranges dataframe.
        self.side_penetration_ranges = pd.read_csv(side_penetration_ranges_path, index_col='armor', na_values='---',
                                                   dtype=float)

        # Define the path for the deck penetration ranges table.
        if self.caliber >= 5.5:
            deck_penetration_ranges_path = "{}{}_deck_penetration_ranges.csv".format(fire_effect_tables_path,
                                                                                     self.designation)

            # Create a deck penetration ranges dataframe.
            self.deck_penetration_ranges = pd.read_csv(deck_penetration_ranges_path, index_col='armor', na_values='X',
                                                       dtype=float)

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

    def return_rate_of_fire(self, target_range):
        """Returns the rate of fire for the gun at a given range."""
        if target_range > self.maximum_range:
            return 0
        else:
            return self.rate_of_fire[self.designation][target_range]

    def return_hit_value(self, target_size, penetrative):
        if penetrative:
            if target_size == "submarine":
                return self.penetrative_values[target_size][self.caliber]
            else:
                return self.penetrative_values["large, intermediate, small, destroyer"][self.caliber]

        else:
            return self.non_penetrative_values[target_size][self.caliber]

    def return_side_penetration(self, armor, deflection, target_range):
        # If armor is thicker than the range tables predict, return False.
        armor_values = self.side_penetration_ranges.index
        if armor > max(armor_values):
            return False

        # Else.
        # Round to the nearest 15 degrees and obtain the appropriate column.
        if deflection > 90:
            deflection -= (deflection // 90) * 90

        deflection = round(deflection / 15) * 15
        if deflection == 90 or deflection == 0:
            deflection = "90 or 0"
        elif deflection == 75 or deflection == 15:
            deflection = "75 or 15"
        elif deflection == 60 or deflection == 30:
            deflection = "60 or 30"
        else:
            deflection = "45"

        # Check for nearest armor value.
        if armor not in armor_values:
            armor = min(armor_values, key=lambda x: abs(x-armor))

        # Check whether a shot would penetrate at that range and deflection.
        if pd.isnull(self.side_penetration_ranges.loc[armor, deflection]):
            return True

        if target_range <= self.side_penetration_ranges.loc[armor, deflection]:
            return True

        else:
            return False

    def return_deck_penetration(self, armor, target_range):
        # Deck penetration only applies to guns 5.5 inches or larger.
        if self.caliber < 5.5:
            return False

        else:
            armor_values = self.deck_penetration_ranges.index
            # Return false if the armour is thicker than what is listed in the penetration tables.
            if armor > max(armor_values):
                return False
            # Likewise, return True if the armour is thinner than the minimum value listed.
            if armor < min(armor_values):
                return True

            # Else.
            # Check for the nearest armor value.
            if armor not in armor_values:
                armor = min(armor_values, key=lambda x: abs(x - armor))

            # Return false if the range listed for that armor value is NAN.
            if pd.isnull(self.deck_penetration_ranges.loc[armor, "target_range"]):
                return False

            # Else.
            if target_range >= self.deck_penetration_ranges.loc[armor, "target_range"]:
                return True

            else:
                return False


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
        # General data
        self.name = name
        self.hull_class = hull_class
        self.size = size
        self.life = self.hit_points = self.starting_hit_points = life
        self.status = self.hit_points / self.starting_hit_points
        self.side = side
        self.deck = deck

        # Armament data
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

        # Own motion data
        self.initial_speed = self.current_speed = None
        self.initial_course = self.current_course = None

        # Target data
        self.remainder_hits = 0

        self.previous_target_data = pd.DataFrame(columns=["firing_group", "target_group", "target_name", "fire",
                                                          "allocated_turrets", "target_bearing", "target_range",
                                                          "evasive", "target_deflection", "penetration"])
        self.target_data = pd.DataFrame(columns=["firing_group", "target_group", "target_name", "fire",
                                                 "allocated_turrets", "target_bearing", "target_range", "evasive",
                                                 "target_deflection", "penetration"])

        # Incoming fire data
        self.incoming_fire = pd.DataFrame(columns=["ship_name", "guns_firing", "caliber", "range"])

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

    def return_base_hits(self, target_size, target_range, target_bearing, spot_type):
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
        rate_of_fire = self.primary_armament.return_rate_of_fire(target_range)
        base_to_hit = self.primary_armament.return_hit_percentage(target_size, target_range, spot_type)
        base_hits = salvo_size * rate_of_fire * base_to_hit

        return base_hits

    def target(self, firing_side, firing_group, target_group, target_ships, fire, target_range, target_bearing, evasive,
               target_deflection):
        target_list = []
        if firing_side == "side_a":
            for ship in target_ships:
                target_list.append(side_b.groups[target_group].ships[ship])

        elif firing_side == "side_b":
            for ship in target_ships:
                target_list.append(side_a.groups[target_group].ships[ship])

        for ship in target_list:
            penetration = self.primary_armament.return_side_penetration(ship.side, target_deflection, target_range)
            self.target_data.loc[ship.name] = (firing_group, target_group, ship.name, fire, 0, target_bearing,
                                               target_range, evasive, target_deflection, penetration)

    def return_first_correction(self, target):
        """Returns the first correction to gunfire – a ratio which reduces rate of fire. It begins at a value of 1
        (no reduction) and diminishes in steps of one tenth depending on circumstances affecting gunnery.

        :return float: the first correction as a ratio (0 to 1) applied to rate of fire.
        """

        # The first correction starts at 1.
        first_correction = 1

        # F-49: Modify rate of fire by ship status.
        # status_lost = round(1 - math.ceil(self.status * 10) / 10, 1)
        # first_correction -= status_lost
        first_correction *= self.status

        # F-15: Check whether range has to be established.
        # First check whether the target has been fired at before for one full move.
        if (target not in self.previous_target_data.index or
                (target in self.previous_target_data.index and not self.previous_target_data["fire"][target])):
            target_group = self.target_data["target_group"][target]
            if ((self.previous_target_data['target_group'] == target_group) &
               self.previous_target_data['fire']).any():
                print("Fire shifted!")
                first_correction -= 0.3

            else:
                print("Opening fire!")
                # Keep track of whether fire is being opened, as it affects other rules.
                opening_fire = True
                target_range = self.target_data["target_range"][target]
                if target_range > 25:
                    first_correction -= 1
                elif target_range >= 21:
                    first_correction -= 0.8
                elif target_range >= 16:
                    first_correction -= 0.6
                elif target_range >= 11:
                    first_correction -= 0.4
                elif target_range >= 6:
                    first_correction -= 0.2

            # PENDING: implement firing at a different target in the same formation.

        # F-18: Check whether fire has been obscured for less than one move, and if so reduce firepower proportionally.
        # This rule is not implemented directly. If anything has interfered with rate of fire for less than three
        # minutes during a given move, it should be specified in the "first correction modifier" for the event in the
        # fire events files.

        return round(first_correction, 2)

    # This function is temporary and will be implemented somewhere else.
    def return_stochastic_hits(self, target_size, target_range, target_bearing, spot_type):
        salvo_size = self.calculate_primary_salvo_size(target_bearing)
        rate_of_fire = self.primary_armament.return_rate_of_fire(target_range)
        total_shots = (salvo_size * rate_of_fire) + self.remainder_hits
        self.remainder_hits = total_shots - int(total_shots)
        total_shots = int(total_shots)
        base_to_hit = self.primary_armament.return_hit_percentage(target_size, target_range, spot_type)
        hits = sum([1 for _ in range(total_shots) if random.random() < base_to_hit])

        return hits


class Group:
    """A temporary implementation of the Group class, made only to enable those firepower correction rules which require
    knowing whether ships are adjacent.
    """
    def __init__(self, name, ships, group_type, formation=True):
        self.name = name
        self.ships = ships
        self.group_type = group_type
        self.formation = formation


class Side:
    """A temporary implementation of the Side class, made only to enable looking up a certain group for targeting."""
    def __init__(self, name, groups):
        self.name = name
        self.groups = groups


# Test ships (Australia)
sydney = Ship("Sydney", "CL", "small", 3.17, 3, 2, "6-in-50", 8, 4, 2, 2, 45, "NA", "NA", "NA", "NA", "NA", "NA",
              "B 21 in", "S", 2, 2)
brisbane = Ship("Brisbane", "CL", "small", 3.17, 3, 2, "6-in-50", 8, 4, 2, 2, 45, "NA", "NA", "NA", "NA", "NA", "NA",
                "B 21 in", "S", 2, 2)

# Test ship motion data
sydney.initial_speed = brisbane.initial_speed = 12
sydney.current_speed = brisbane.current_speed = 14
sydney.initial_course = brisbane.initial_course = 90
sydney.current_course = brisbane.current_course = 120

# Test ships (Germany
emden = Ship("Emden", "CL", "small", 2.37, 3, 1.2, "4-in-45-A", 10, 5, 2, 2, 30, "NA", "NA", "NA", "NA", "NA", "NA",
             "B 17.7 in", "S", 2, 2)
dresden = Ship("Dresden", "CL", "small", 2.37, 3, 1.2, "4-in-45-A", 10, 5, 2, 2, 30, "NA", "NA", "NA", "NA", "NA", "NA",
               "B 17.7 in", "S", 2, 2)

# Test ship motion data
emden.initial_speed = dresden.initial_speed = 10
emden.current_speed = dresden.current_speed = 15
emden.initial_course = dresden.initial_course = 80
emden.current_course = dresden.current_course = 90

# Test group ship dictionaries
side_a_group_ships = {"Sydney": sydney, "Brisbane": brisbane}
side_b_group_ships = {"Emden": emden, "Dresden": dresden}

# Test groups
side_a_groups = {"Brisbane and Sydney": Group("Brisbane and Sydney", side_a_group_ships, False)}
side_b_groups = {"Emden and Dresden": Group("Emden and Dresden", side_b_group_ships, True)}

# Test sides
side_a = Side("Australia", side_a_groups)
side_b = Side("Germany", side_b_groups)

# Test gun
test_gun = Gun("6-in-50")

# Target Sydney as Emden
emden.target("side_b", "Emden and Dresden", "Brisbane and Sydney", ["Brisbane"], False, 12, 85, True, 90)
# Advance one turn
emden.previous_target_data = emden.target_data.copy()
# Target again, firing this time
emden.target("side_b", "Emden and Dresden", "Brisbane and Sydney", ["Brisbane"], True, 10, 70, True, 75)

# Check range rate on target
range_rate = abs(emden.target_data["target_range"]["Brisbane"] - emden.previous_target_data["target_range"]["Brisbane"])
print(range_rate)

# Print target data
with pd.option_context('display.max_rows', 5, 'display.max_columns', None, 'display.width', None):
    print(emden.previous_target_data)
    print(emden.target_data)

print(emden.return_first_correction("Brisbane"))
