############################################
# Instructions for Tactical Exercises 1921 #
#  © Alvaro Radigales, 2021 - MIT licence  #
############################################

# A Python implementation of the Royal Navy's 1921 wargame rules. It is designed to create a model of a battle from a
# series of external, human-readable files, and then resolve it by playing out the action at one-minute intervals. The
# battle outcome can be logged or plotted for analysis.

import configparser
import csv
import datetime
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns

####################
# PARSER FUNCTIONS #
####################

# These functions open and parse the external files needed for the model to run. The files contain model settings,
# battle data, fleet lists, gun specifications etc. Please note that the Royal Navy's 1921 model is relatively simple
# and it only uses a small fraction of the information in the input files. Other wargame rule sets, such as the Naval
# War College's 1922 Maneuver Rules, may use all parameters.


def parse_model_settings():
    """Parse the model_settings.cfg file. This file contains global simulation settings such as gun range interpolation
    or output file options.
    """
    # Initialise the parser.
    model_settings = configparser.ConfigParser()
    # Set the config file name.
    model_settings_file = "model_settings.cfg"
    # Read the file and return the parser object.
    model_settings.read(model_settings_file)

    return model_settings


def parse_battle_cfg(battle_id_string):
    """Parse the config file for a battle from that battle's ID string. The file contains information on conditions
    affecting the entire battle: name, location, date and time, identity of the belligerents, weather and visibility
    conditions, and paths to fleet and gunnery data. Returns a ConfigParser reader object.
    """
    # Initialise the parser.
    battle_config = configparser.ConfigParser()
    # Build the battle data path string.
    battle_data_path = "battle_data/{}/{}.cfg".format(battle_id_string, battle_id_string)
    # Read the file and return the parser object.
    battle_config.read(battle_data_path)

    return battle_config


def parse_group_data(battle_id_string):
    """Parse the group data file for a battle from that battle's ID string.This is a CSV file containing one row for
    each group of ships in each of the two sides of the battle. The row contains the name of the group (used in
    defining fire events, to know which group fires at which), its members (as a string of comma-separated ship names)
    and its type ('capital' for battleships and battlecruisers, 'light' for groups made up of light division ships).
    This last distinction is important because the Royal Navy's 1921 rules use different equations to determine
    equivalent hitting power for the two: capital ship guns are all converted to 15-inch hits, and light division guns
    are all converted to 6-inch hits. These two equations are not compatible, so the model cannot really compare the
    relative firepower of groups of different types.

    Returns a tuple of two dictionaries: one with side A's groups, and one with side B's groups"""

    # Build the group data paths.
    group_data_path = "battle_data/{}/".format(battle_id_string)
    side_a_path = group_data_path + "side_a_groups.csv"
    side_b_path = group_data_path + "side_b_groups.csv"
    # Make the group dictionary for side A.
    side_a_group_dictionary = {}
    with open(side_a_path) as input_file:
        side_a_groups = csv.reader(input_file, delimiter=',')
        next(side_a_groups, None)
        for row in side_a_groups:
            name = row[0]
            ships = row[1].split(",")
            group_type = row[2]
            side_a_group_dictionary[name] = (ships, group_type)
    # Make the group dictionary for side B.
    side_b_group_dictionary = {}
    with open(side_b_path) as input_file:
        side_b_groups = csv.reader(input_file, delimiter=',')
        next(side_b_groups, None)
        for row in side_b_groups:
            name = row[0]
            ships = [ship.strip() for ship in row[1].split(",")]
            group_type = row[2]
            side_b_group_dictionary[name] = (ships, group_type)

    # Return both dictionaries.
    return side_a_group_dictionary, side_b_group_dictionary


def parse_battle_events(battle_id_string):
    """Parse the event data files for both belligerents in a battle from that battle's ID string. These are CSV files
    detailing all fire actions in an engagement (which groups fire at which, when and for how long, and any conditions
    that might affect gunnery. The function outputs two ordered lists of events (one for each belligerent) to build
    the battle timeline from.
    """

    # Build the event data file paths.
    event_data_path = "battle_data/{}/".format(battle_id_string)
    side_a_event_file = event_data_path + "side_a_events.csv"
    side_b_event_file = event_data_path + "side_b_events.csv"

    # Build the event list for side A.
    side_a_events = []
    with open(side_a_event_file) as input_file:
        side_a_event_table = csv.reader(input_file, delimiter=',')
        next(side_a_event_table, None)
        for row in side_a_event_table:
            # Check whether the event is a fire event, and if so, add it to the list.
            if row[3] == "TRUE":
                firer = row[4]
                target = row[5]
                target_range = float(row[9]) * 1000
                start = int(row[1])
                duration = int(row[2])
                target_bearing = int(row[10])
                modifier = float(row[14])

                side_a_events.append((firer, target, target_range, start, duration, target_bearing, modifier))

    # Build the event list for side B.
    side_b_events = []
    with open(side_b_event_file) as input_file:
        side_b_event_table = csv.reader(input_file, delimiter=',')
        next(side_b_event_table, None)
        for row in side_b_event_table:
            # Check whether the event is a fire event, and if so, add it to the list.
            if row[3] == "TRUE":
                firer = row[4]
                target = row[5]
                target_range = float(row[9]) * 1000
                start = int(row[1])
                duration = int(row[2])
                target_bearing = int(row[10])
                modifier = float(row[14])

                side_b_events.append((firer, target, target_range, start, duration, target_bearing, modifier))

    return side_a_events, side_b_events


def parse_fleet_lists(battle_id_string):
    """Parse the fleet lists for the two belligerents. These are CSV files containing the parameters of all ships used
    in the model, listed by name. The paths to these files are determined in each battle's config file.

    Returns a tuple of dictionaries: one with side A's fleet lists, and another for B's.
    """

    # Define the fleet list paths from the battle config file.
    side_a_fleet_path = parse_battle_cfg(battle_id_string)["Data files"]["side_a_ships"]
    side_b_fleet_path = parse_battle_cfg(battle_id_string)["Data files"]["side_b_ships"]

    # Open and parse side A's fleet list.
    with open(side_a_fleet_path) as input_file:
        side_a_fleet_reader = csv.reader(input_file, delimiter=',')
        next(side_a_fleet_reader, None)
        side_a_fleet_dictionary = {}
        for row in side_a_fleet_reader:
            side_a_fleet_dictionary[row[0]] = row

    # Open and parse side B's fleet list.
    with open(side_b_fleet_path) as input_file:
        side_b_fleet_reader = csv.reader(input_file, delimiter=',')
        next(side_b_fleet_reader, None)
        side_b_fleet_dictionary = {}
        for row in side_b_fleet_reader:
            side_b_fleet_dictionary[row[0]] = row

    # Return both fleet lists as dictionaries.
    return side_a_fleet_dictionary, side_b_fleet_dictionary


def parse_gun_data(battle_id_string):
    """Build a dictionary of gun parameters from external CSV files

    Arguments:
        - battle_id_string: the battle's ID string, used to load the config file containing the gun data directories.

    Output:
        A dictionary of dictionaries, with the following keys:
            - "capital_ship_guns"
            - "secondary_guns"
            - "light_cruiser_guns"
            - "destroyer_guns"

        Each key contains a gunnery table in dictionary format, with the following structure:

        - Key: the gun designation (e.g. '13.5 in V' or '12 in XI')
        - Value: a list of parameters, in the order:
            * caliber (in inches)
            * max_ange (maximum range in yards)
            * long_to_hit (chance to hit per gun and minute at long range)
            * long_min (minimum range considered to be long)
            * effective_to_hit (chance to hit per gun and minute at effective range)
            * effective_min (minimum range considered to be effective)
            * short_to_hit (chance to hit per gun and minute at short range)

    A new instance of the Gun class is created for each ship from these values. Changing an individual ship's gun (for
    example to model a certain gun designation not present in the tables) will NOT affect other ships using the same
    gun designation. Any global changes must be made in the source tables, and not in the program itself.
    """

    # Initialise the gun dictionary.
    gun_tables = {}
    # Set the gun data directory from the battle config file.
    gun_data_directory = parse_battle_cfg(battle_id_string)["Data files"]["instructions_1921_gun_data"]
    gun_data_files = ["capital_ship_guns.csv", "secondary_guns.csv", "light_cruiser_guns.csv", "destroyer_guns.csv"]
    for gun_data_file in gun_data_files:
        gun_table = {}
        gun_data_file_path = gun_data_directory + gun_data_file
        # Read the data file and populate the dictionary with the values for each gun.
        with open(gun_data_file_path) as input_file:
            reader = csv.reader(input_file, delimiter=",")
            next(reader)
            for row in reader:
                gun_data = list(row)
                gun_table_entry = gun_data[:2]
                gun_table_entry += list(map(float, gun_data[2:]))
                gun_table[gun_data[0]] = gun_table_entry
        gun_tables[gun_data_file[:-4]] = gun_table

    # Return the dictionary
    return gun_tables


#######################
# CONFIGURATION FLAGS #
#######################

# Global settings determining how the model should run.

# Interpolate hit values at 1000-yard range increments from the original tables.
INTERPOLATE = parse_model_settings()["Gunnery"].getboolean('interpolation')
# Output battle outcome to the interpreter console.
CONSOLE_OUTPUT = parse_model_settings()["Reports"].getboolean('console_output')
# Save detailed battle report to CSV files in the 'reports' directory.
REPORT = parse_model_settings()["Reports"].getboolean('export_results')
# Draw a chart plotting the battle strengths of the two sides throughout the battle.
DRAW_PLOT = parse_model_settings()["Reports"].get('draw_plot')
# Automatically save the above chart in the 'reports' directory
SAVE_PLOT = parse_model_settings()["Reports"].get('save_plot')
# Save a verbose text description of all actions per round to the 'reports' directory
VERBOSE = parse_model_settings()["Reports"].get('verbose')


##################################
# BATTLE LOGIC CLASS DEFINITIONS #
##################################

# Definitions of the Gun, Ship, Group, Side and Battle classes and associated functions.
# These represent the core logic of the model, and run all relevant battle calculations.


class Gun:
    """A naval gun, as mounted on a ship.

    Attributes:
        - name: the gun designation in the 1921 tables.
        - mount: the gun mount type (capital, secondary, cruiser, destroyer) in the 1921 tables.
        - caliber: the caliber of the gun in inches.
        - max_range: maximum range in yards.
        - long_to_hit: chance to hit per gun per minute at long range.
        - long_min: minimum range in yards considered to be long range.
        - effective_to_hit: chance to hit per gun per minute at effective range.
        - effective_min: minimum range in yards considered to be effective.
        - short_to_hit: chance to hit per gun per minute at short range.
        - first_regression_term: first term of the polynomial regression equation to calculate hits per minute at an
        arbitrary range.
        - second_regression_term: second term of the polynomial regression equation to calculate hits per minute at
        an arbitrary range.
        - third_regression_term: third term of the polynomial regression equation to calculate hits per minute at
        an arbitrary range.

    Methods:
        - return_to_hit(target_range): returns the base number of hits per gun per minute at the range provided.
        - return_damage_conversion_factor(): the 1921 Royal Navy rules convert all hits to two standard calibres:
        6-inch hits for light ships, and 15-inch hits for battlecruisers and battleships. This method returns the factor
        needed to convert a gun's hits to the equivalent 6-inch or 15-inch hits
        - return_equivalent_damage(target_range): returns the return_to_hit() number multiplied by the conversion
        factor. Essentially combines the two methods above into one.
    """

    def __init__(self, name, mount, caliber, max_range, long_to_hit, long_min, effective_to_hit, effective_min,
                 short_to_hit, first_regression_term, second_regression_term, third_regression_term):
        self.name = name
        self.mount = mount
        self.caliber = max(0, caliber)
        self.max_range = max_range
        self.long_to_hit = long_to_hit
        self.long_min = long_min
        self.effective_to_hit = effective_to_hit
        self.effective_min = effective_min
        self.short_to_hit = short_to_hit
        self.first_regression_term = first_regression_term
        self.second_regression_term = second_regression_term
        self.third_regression_term = third_regression_term

    def return_to_hit(self, target_range, interpolate=INTERPOLATE):
        """Return the chance to hit (per gun and minute) for a given range. If the target is out of range, return 0."""
        if target_range > self.max_range or target_range < 0:
            return 0
        else:
            if interpolate:
                base_hits_per_minute = self.first_regression_term * target_range ** 2 \
                                       + self.second_regression_term * target_range \
                                       + self.third_regression_term
                return max(base_hits_per_minute, 0)
            elif not interpolate:
                if target_range > self.long_min:
                    return self.long_to_hit
                elif target_range > self.effective_min:
                    return self.effective_to_hit
                elif target_range >= 0:
                    return self.short_to_hit

    def return_damage_conversion_factor(self):
        """The 1921 Royal Navy rules convert all hits to an equivalent number of 6-inch hits (light guns) or 15-inch
        hits (heavy guns). This function returns the factor needed for the conversion.
        """
        # Conversion factor to 6-inch hits for light gun calibers
        if self.caliber <= 9.5:
            # The conversion factors below are as stated in the original 1921 rules
            if self.caliber == 4:
                damage_equivalent = 1 / 3
            elif self.caliber == 4.7:
                damage_equivalent = 1 / 2
            elif self.caliber == 6:
                damage_equivalent = 1
            elif self.caliber == 7.5:
                damage_equivalent = 3
            # All other light calibers are determined through interpolation
            # We used power regression (R squared value of 0.9751)
            else:
                damage_equivalent = 0.0025 * (self.caliber ** 3.4419)
        # Conversion factor to 15-inch hits for heavy gun calibers
        elif self.caliber > 9.5:
            # Here we just use an equation for all cases because damage for big guns scales linearly
            damage_equivalent = 1 / ((-self.caliber / 3) + 6)
        else:
            raise ValueError("Caliber must be a positive real number")

        return damage_equivalent

    def return_equivalent_damage(self, target_range):
        """Return the damage dealt by the gun over one minute at a given range, adjusted to 15-inch (capital guns)
        or 6-inch (light guns) equivalent hits.

        Arguments:
        - target_range: the range to the target in yards (integer).
        """
        equivalent_damage = self.return_to_hit(target_range) * self.return_damage_conversion_factor()
        return equivalent_damage


class Ship:
    """
    A ship object. Keeps track of its damage status and contains gun objects.

    Attributes:
        Input from file:
        - name: the name of the ship (string).
        - hull_class: "battleship", "battle cruiser", "light cruiser", "flotilla leader" or "destroyer" (string).
        - main_armament_type: the model of gun used in the ship's main battery (gun object).
        - main_armament_count: the total number of guns of the main type carried by the ship (int).
        - main_armament_broadside: the number of guns the ship can bring to bear in either broadside (int).
        Calculated by the program:
        - minimum_to_damage: the minimum caliber a gun must have to damage the ship.
        - staying_power: the ship's staying power (int).
            * For battleships and battle cruisers, measured in 15-inch hits.
            * For light cruisers and smaller classes, measured in 6-inch hits.
        - hit_points: begins equal to staying power. Used to keep track of damage (float).
        - starting_hit_points: stores a ship's hit points at the start of each simulation pulse.
        - status: 1 means undamaged, 0 means out of action / firepower kill (float).
        - hits_received: a record of hits received by caliber until becoming a firepower kill (dictionary).
            * Hits received are saved as a float in case the decimal part (partial hits) is needed for analysis.

    Methods:
        - fire(target, target_range, distribution=1, salvo_size, modifier): fires at a target ship. Calculates the
        number of (normalised) hits in one minute at a given range. Can be modified by three factors:
            * Distribution: fraction of hits actually applied to that specific ship. This is used when dividing fire
            among many targets.
            * Salvo size: number of guns bearing. Used to reflect circumstances in which the firing ship might not
            be broadside-on.
            * Modifier: an arbitrary modifier used to reflect any other factors not considered in the simulation.
        - damage(points): apply a number of damage points to the ship. These damage points are expressed in 6-inch hits
        (light division) or 15-inch hits (battlecruisers and battleships). Damage does not affect the ship's firepower
        until applied by use of the ship's update() method.
        - record_hits(caliber, hits): record the number of hits of a given caliber taken by the ship. This record is
        kept in the hits_received{} dictionary. It has no effect in the simulation. The method exists for analytical
        purposes only.
        - update(): applies all pending damage to the ship and refreshes its status. Applied damage affects the ship's
        offensive capabilities.
    """

    def __init__(self, name, hull_class, main_armament_type, main_armament_count, main_armament_broadside,
                 main_armament_bow, main_armament_stern, main_armament_end_arc):
        self.name = name
        self.hull_class = hull_class
        self.main_armament_type = main_armament_type
        self.main_armament_count = int(main_armament_count)
        self.main_armament_broadside = int(main_armament_broadside)
        self.main_armament_bow = int(main_armament_bow)
        self.main_armament_stern = int(main_armament_stern)
        self.main_armament_end_arc = int(main_armament_end_arc)
        self.staying_power = self.main_armament_count
        # Calculate the staying power multiplier for battleships based on main gun calibre.
        if self.hull_class in ("BB", "OBB"):
            if self.main_armament_type.caliber <= 12:
                self.staying_power *= 1
            elif self.main_armament_type.caliber <= 14:
                self.staying_power *= 2
            elif self.main_armament_type.caliber <= 15:
                self.staying_power *= 3
            else:
                self.staying_power *= 3.25
            # Set the minimum caliber of the gun that can damage a battleship.
            self.minimum_to_damage = 12
        # Calculate the staying power multiplier for battle cruisers based on main gun calibre.
        elif self.hull_class in ["CC", "OCC"]:
            if self.main_armament_type.caliber <= 12:
                self.staying_power *= 0.75
            elif self.main_armament_type.caliber <= 13.5:
                self.staying_power *= 1.75
            elif self.main_armament_type.caliber <= 15:
                self.staying_power *= 2.5
            else:
                self.staying_power *= 2.75
            # Set the minimum caliber of the gun that can damage a battle cruiser.
            self.minimum_to_damage = 12
        # Calculate the staying power multiplier for light cruisers based on main gun calibre.
        elif self.hull_class in ["CA", "OCA", "CL", "OCL"]:
            if self.main_armament_type.caliber <= 4:
                self.staying_power *= 4
            elif self.main_armament_type.caliber <= 6:
                self.staying_power *= 8
            else:
                self.staying_power *= 9
            # Set the minimum caliber of the gun that can damage a battleship.
            self.minimum_to_damage = 4
        # Calculate the staying power multiplier for light squadron ships based on main gun calibre.
        elif self.hull_class in ["DL", "DD", "ODD", "DM"]:
            self.staying_power *= 1
            # Note that a value of 1 in the above line will not change staying power at all. The
            # line is left here for clarity and in case one needs to experiment with the value.
            # Set the minimum caliber of the gun that can damage a light squadron ships.
            self.minimum_to_damage = 4
        # Raise an exception if attempting to create a ship without a valid hull class.
        else:
            raise ValueError("Wrong ship class definition")

        # Set the ship's initial hit points and status
        self.hit_points = self.starting_hit_points = self.staying_power
        self.status = 1
        self.hits_received = {}

    def fire(self, target, target_range, distribution=1, bearing=90, modifier=1):
        """Fire at a target ship. This function records the hits received by the target, then converts them to
        equivalent 6-inch or 14-inch hits and applies the resulting damage.

        Arguments:
        - target: the target ship (Ship).
        - distribution: fraction of the firing ship's firepower directed at the target (fraction). Defaults to 1,
        meaning the full available firepower is used. Changing this number is the standard way of splitting fire
        between two or more targets. See the Group class fire() documentation to understand why this is done.
        - salvo_size: the number of guns firing, passed to the Ship class fire method. Defaults to the broadside
        value of each ship.
        - modifier: a multiplier to firing effectiveness (fraction). Defaults to 1. This argument is used to introduce
        variables not explicitly reflected in the 1921 rules and left instead to the discretion of the umpire, such as
        visibility, crew training, fire direction differences, etc.
        """

        firing_caliber = self.main_armament_type.caliber
        base_to_hit = self.main_armament_type.return_to_hit(target_range)

        # Calculate how many guns are bearing on the target.
        # Begin by normalising the angle.
        if bearing > 180:
            bearing = 180 - (bearing % 180)
        # Check the arc within which the target lies.
        if bearing < self.main_armament_end_arc:
            salvo_size = self.main_armament_bow
        elif bearing > (180 - self.main_armament_end_arc):
            salvo_size = self.main_armament_stern
        else:
            salvo_size = self.main_armament_broadside

        # Calculate the number of hits in a one-minute pulse taking all modifiers into account
        # Check if any special rules apply due to target size
        # Turret guns against light division
        if self.main_armament_type.mount == "capital":
            if target.hull_class == "light cruiser":
                modifier *= 1 / 3
            elif target.hull_class in ("flotilla leader", "destroyer"):
                modifier *= 0.125
        # Cruiser guns against destroyers and flotilla leaders
        elif self.main_armament_type.mount == "cruiser" and target.hull_class in ("flotilla leader", "destroyer"):
            modifier *= 0.2
        # Destroyer / flotilla leader guns against light cruisers
        elif self.main_armament_type.mount == "destroyer" and target.hull_class == "light cruiser":
            modifier *= 2
        # Secondary guns against destroyers and flotilla leaders
        elif self.main_armament_type == "secondary" and target.hull_class in ("flotilla leader", "destroyer"):
            modifier *= 0.2
        hits = base_to_hit * salvo_size * distribution * modifier * self.status
        # Record the hits on the target
        target.record_hits(firing_caliber, hits)
        # Apply damage to the target
        # Check if turret guns are firing on a light ship. If so, apply special damage as per table B of the rules
        if firing_caliber > 9.5 and target.hull_class in ("light cruiser", "flotilla leader", "destroyer"):
            # When targeting light cruisers
            if target.hull_class == "light cruiser":
                if target.main_armament_type.caliber >= 7.5:
                    # Damage the target for 1/4 of its total staying power per hit
                    target.damage(hits * (target.staying_power / 4))
                elif target.main_armament_type.caliber >= 6:
                    # Damage the target for 1/3 of its total staying power per hit
                    target.damage(hits * (target.staying_power / 3))
                elif target.main_armament_type.caliber >= 4:
                    # Damage the target for 1/2 of its total staying power per hit
                    target.damage(hits * (target.staying_power / 2))
            # When targeting flotilla leaders or destroyers
            else:
                # Knock the target out after one hit
                target.damage(hits * target.staying_power)
        # If not, check whether the caliber is large enough to affect the target, and apply damage normally
        else:
            if firing_caliber >= target.minimum_to_damage:
                target.damage(hits * self.main_armament_type.return_damage_conversion_factor())

    def damage(self, damage_points):
        """ Damages the ship by a given number of points. One point is either a 6-inch (light division ships) or 15-inch
         (battlecruisers and battleships) hit equivalent. This damage is not applied (does not affect a ship's status
         and hence firepower) until the update() function is run.

        Arguments:
            - damage_points: the number of damage points to inflict on the target's HP pool, normalised to
            6-inch or 15-inch hits (float).
        """
        # Reduce the target ship's HP pool by the number given, making sure it never goes into the negative.
        self.hit_points -= min(damage_points, self.hit_points)

    def record_hits(self, caliber, hits):
        """Record a number of hits by a gun of a given caliber in the 'hits_received' dictionary."""
        # Record hits only if the ship is not already knocked out
        if self.hit_points > 0:
            # If the ship has already received hits of the caliber given, add to the existing record
            if caliber in self.hits_received:
                self.hits_received[caliber] += hits
            # Else, make a new entry
            else:
                self.hits_received[caliber] = hits

    def update(self):
        """ Applies pending damage. Sets starting_hit_points to the current value and updates status."""
        self.starting_hit_points = self.hit_points
        self.status = self.hit_points / self.staying_power

    def return_firepower(self, target_range, firing_arc="broadside"):
        """Return the firepower (15-inch or 6-inch hit equivalents) at a given range and firing arc.

        Attributes:
            - target_range: the range to the target in thousands of yards (int).
            - firing_arc: bow, stern, or broadside. Defaults to broadside.
        """

        base_to_hit = self.main_armament_type.return_to_hit(target_range)

        if firing_arc == "bow":
            salvo_size = self.main_armament_bow
        elif firing_arc == "stern":
            salvo_size = self.main_armament_stern
        else:
            salvo_size = self.main_armament_broadside

        hits = base_to_hit * salvo_size

        equivalent_hits = hits * self.main_armament_type.return_damage_conversion_factor()

        return equivalent_hits

    def __str__(self):
        """String override method. Return a summary of a ship's stats"""
        name = self.name
        hull = self.hull_class
        guns = self.main_armament_count
        gun_type = self.main_armament_type.caliber
        integrity = self.status * 100
        return "{} ({}) {} x {} in, {}%".format(name, hull, guns, gun_type, integrity)


class Group:
    """A group of ships, consisting of one ship or more. All ships in the simulation must belong to a group,
    even if they are the group's sole member. Groups behave according to the following rules:

    - Groups outnumbering their target group fire with a penalty to their accuracy as defined in the 1921 rules.
    - When firing, each individual ship in the group fires in turn, targeting only the enemy ships it can damage.
    - Damage is distributed among all target ships proportionally to their remaining staying power. In other words,
    all target ships are aggregated into one for damage purposes.

    Note that the same ship can be registered in more than one group. A ship may receive fire as part of a large
    group and individually (in a different one-ship group) during the same battle. Hence, in this simulation,
    aggregation is not the norm, but merely another tool at the user's disposal.

    Attributes:
        - name: the name of the group (string).
        - members: a list of ships belonging to the group (list).
        - staying_power: the sum total of the staying power of all members (float)
        - starting_hit_points: the sum total of the remaining hit points of all members at the beginning of a time pulse
        (float). This number is updated at the end of every pulse.
        - hit_points: the sum total of the remaining hit points of all members at any given time (float).
        - status: a fraction indicating the level of damage received by a ship. A value of 1 means the ship is intact,
        while a value of 0 means it is out of action (fraction).

    Methods:
        - add_ship(ship): add a ship to the group. Groups are normally initialised with members, but should one need
        to incorporate another ship mid-battle this would be the way to do it.
        - fire(target_group, target_range, salvo_size, modifier): fire at another group. Makes each individual ship
        in the firing group use its fire() method and distributes damage among all the ships in the target group,
        proportional to their remaining hit points. See the Ship class fire() method for more information.
        - update(): applies pending damage to all ships in the group, and refreshes the group's status.
    """

    def __init__(self, name, members, group_type):
        self.name = name
        self.members = members
        self.group_type = group_type
        self.staying_power = sum(ship.staying_power for ship in members)
        self.hit_points = self.starting_hit_points = self.staying_power
        self.status = 1

    def add_ship(self, ship):
        """Add a ship object to the group members list.

        Arguments:
            - ship: a Ship object to add to the members list.
        """
        self.members.append(ship)
        self.staying_power += ship.staying_power
        self.hit_points += ship.hit_points
        self.status = self.hit_points / self.staying_power

    def fire(self, target_group, target_range, salvo_size=None, modifier=1):
        """Fire at the target group at the specified range. When the target group consists of more than one ship,
        damage is treated as aggregated: first, the program determines the percentage of the target group's total
        hit points that would be damaged by the salvo. Then, each individual ship in the group is damaged by this
        same percentage.

        Arguments:
            - target_group: the enemy group to fire at (Group object).
            - target_range: the range at which the enemy group is.
            - salvo size: the number of guns firing, passed to the Ship class fire method. Defaults to the broadside
            value of each ship.
            - modifier: an arbitrary multiplier to firepower, passed to the Ship class fire method. Defaults to 1.
            This argument is used to introduce variables not explicitly reflected in the 1921 rules and left instead
            to the discretion of the umpire, such as visibility, crew training, fire direction differences, etc.
        """

        # If the firing group is larger than the target group, reduce accuracy to reflect the shell splashes from
        # different ships getting mixed up and making corrections difficult.
        if len(self.members) > len(target_group.members):
            # Calculate the ratio by which the firing side is superior
            superiority_ratio = len(self.members) / len(target_group.members)
            # The rules give a (lower) equivalent number of firing ships, calculated with the following equation
            equivalent_superiority = (superiority_ratio / 2) + 1
            # Divide this by the actual superiority ratio to get a conversion factor
            concentration_multiplier = equivalent_superiority / superiority_ratio
            # Change the general modifier by the resulting factor
            modifier *= concentration_multiplier
            print(modifier)

        # Distribute fire among the target group's ships proportionally to their remaining hit points.
        if target_group.hit_points > 0:
            fire_distribution = [ship.starting_hit_points / target_group.hit_points
                                 for ship in target_group.members]
        else:
            fire_distribution = [1 / len(target_group.members)] * len(target_group.members)
        for own_ship in self.members:
            for target_number, target_ship in enumerate(target_group.members):
                own_ship.fire(target_ship, target_range, fire_distribution[target_number], salvo_size, modifier)

    def update(self):
        """ Applies pending damage. Sets starting_hit_points to the current value and updates status."""
        for ship in self.members:
            ship.update()
        self.hit_points = sum(ship.hit_points for ship in self.members)
        self.status = self.hit_points / self.staying_power

    def __str__(self):
        """String override method. Return a summary of a group's members and stats"""
        name = self.name
        member_list = ", ".join([ship.name for ship in self.members])
        status = self.status * 100
        return "{} ({}), {}%".format(name, member_list, status)


class Side:
    """One of two opposing sides in a battle, formed by one or more groups.

    Attributes:
        - name: the side's name (string).
        - groups: the ship groups belonging to the side (dictionary).
        - staying_power: the total staying power of all the ships in all groups (float).
        - hit_points: the remaining hit points of all the ships in all groups (float).
        - status: the fraction of remaining hit points for the whole side. A value of 1 means the side is intact, while
        a value of 0 means it is out of action (fraction).
        - fire_events: all the fire events the side is going to carry out in a battle. A fire event is a tuple
        containing a description of a moment in which a group opens fire against another. It is defined by the firing
        group, the target group, the moment it starts, its duration, and the general effectiveness (determined by the
        salvo size and an arbitrary modifier) (list).
        - latest_event: the last minute, counted from the beginning of the battle, during which any fire events of the
        side are taking place. Used in determining the overall duration of the battle (integer).

    Methods:
        - update(): applies any pending damage to all the groups in the side, and refreshes the side's overall status.
        - register_fire_event(firer, target, target_range, start, duration, salvo_size, modifier): adds a fire event
        with all the specified parameters to the side's fire event list. This method is used to populate a battle's
        timeline and specify which groups fire upon which groups, when and how.
    """

    def __init__(self, name, groups):
        self.name = name
        self.groups = groups
        self.staying_power = sum(groups[group].staying_power for group in groups)
        self.hit_points = self.starting_hit_points = self.staying_power
        self.status = 1
        self.fire_events = []
        self.latest_event = 0

    def update(self):
        """Applies pending damage to all groups in the side, and updates hit points and status accordingly.
        This method is run once every time pulse.
        """
        for group in self.groups.values():
            group.update()
        self.hit_points = sum(group.hit_points for group in self.groups.values())
        self.status = self.hit_points / self.staying_power

    def register_fire_event(self, firer, target, target_range, start, duration, target_bearing=90, modifier=1):
        """Add a fire event to the side. Fire events are defined by:
                - firer: the index of the group that is firing (0 = first group, 1 = second group...)
                - target_ the index of the target group in the enemy side (0 = first, 1 = second...)
                - target_range: the range at which the group is firing, in yards.
                - start: the minute at which fire starts.
                - duration: the duration of the action in minutes.
                - salvo_size: a fraction determining how many guns bear (defaults to None meaning full a broadside)
                - modifier: an arbitrary multiplier to firepower, passed to the Group class fire method. Defaults to 1.
            This argument is used to introduce variables not explicitly reflected in the 1921 rules and left instead
            to the discretion of the umpire, such as visibility, crew training, fire direction differences, etc.
        """

        # Check whether this event will finish later than any other of the side's events.
        if start + duration > self.latest_event:
            self.latest_event = start + duration + 1

        # Make a tuple representing all the event's parameters
        new_event = (firer, target, target_range, start, start + duration, target_bearing, modifier)

        # Append the tuple to the list of fire events for the side
        self.fire_events.append(new_event)

    def __str__(self):
        group_names = [group for group in self.groups]
        group_names_string = ", ".join(group_names)
        strength = self.status * 100
        side_string = "{} ({})\nRemaining strength: {}%".format(self.name, group_names_string, strength)
        return side_string


class Battle:
    """A battle between two opposing sides. This class contains the data structures and methods needed to dictate
    which group from which side fires and when.

    Attributes:
        - name: the name of the battle (string).
        - side_a: one of the two sides involved in the battle (Side).
        - side_b: the other side involved in the battle (Side).
        - side_a_timeline: a list of length equal to the number of minutes of battle duration. For each minute, the
        list may contain one or more tuples indicating all the fire events for side A (list).
        - side_b_timeline: same as above, but for side B (list).
        These two timelines are populated automatically upon initialization of a Battle instance, from the fire event
        lists of the sides involved.
        - side_a_staying_power: a list containing the total hit points of side A at each minute of the action, so that a
         graph can be plotted at the end of the battle (list).
        - side_b_staying_power: same as above, but for side B (list).
        - time_pulse: the current minute of the battle. Begins at 0 and is advanced by 1 every time the advance_pulse()
        method is called (integer).

    Methods:
        - advance_pulse(): advances the battle by one minute. This method executes all the fire events pending for the
        current minute, assigning damage to both sides. At the end of the time pulse all pending damage is applied, the
        lists side_a_staying_power and side_b_staying_power are updated, and the status of all ships in both sides is
        refreshed. The variable time_pulse is also increased by one.
        - resolve(): automatically resolves the entire battle, pulse by pulse, until either side is out of action or
        all fire events have been executed.
    """

    def __init__(self, battle_id_string, name, side_a, side_b):
        self.battle_id_string = battle_id_string
        self.name = name
        self.side_a = side_a
        self.side_b = side_b
        # Determine the battle duration.
        self.battle_duration = max(self.side_a.latest_event, self.side_b.latest_event)
        # Initialise fire event timelines for both sides.
        self.side_a_timeline = [[] for _ in range(self.battle_duration)]
        self.side_b_timeline = [[] for _ in range(self.battle_duration)]
        # Initialise the staying power plot for both sides.
        self.side_a_staying_power = [self.side_a.staying_power]
        self.side_b_staying_power = [self.side_b.staying_power]
        # Set the current time pulse to 0.
        self.time_pulse = 0
        # The battle_data attribute gets assigned a Pandas dataframe once the battle is resolved.
        self.battle_data = None
        # Build the path for battle report files.
        self.report_path = 'reports/{}/'.format(self.battle_id_string)

        # Build the timelines for both sides from their event lists.

        # Side A events.
        # If any events exist...
        if len(self.side_a.fire_events) > 0:
            # Deal with each as follows:
            for event in self.side_a.fire_events:
                # Select the minutes of the timeline between the event's start and its end.
                for minute in range(event[3], event[4]):
                    # Add to each minute a tuple containing the firer, target, range, salvo size and fire modifier.
                    self.side_a_timeline[minute].append((event[0], event[1], event[2], event[5], event[6]))

        # Side B events.
        # If any events exist...
        if len(self.side_b.fire_events) > 0:
            # Deal with each as follows:
            for event in self.side_b.fire_events:
                # Select the minutes of the timeline between the event's start and its end.
                for minute in range(event[3], event[4]):
                    # Add to each minute a tuple containing the firer, target, range, bearing and fire modifier
                    self.side_b_timeline[minute].append((event[0], event[1], event[2], event[5], event[6]))

    def advance_pulse(self):
        """Advance the battle by a single one-minute pulse."""
        # Check for side A fire events in this time pulse.
        if len(self.side_a_timeline[self.time_pulse]) > 0:
            # Play out the events by making groups fire at each other as instructed by the event's parameters.
            # Start by iterating over the events.
            for event in self.side_a_timeline[self.time_pulse]:
                self.side_a.groups[event[0]].fire(self.side_b.groups[event[1]], event[2], event[3], event[4])
        # Check for side B fire events in this time pulse.
        if len(self.side_b_timeline[self.time_pulse]) > 0:
            # Play out the events by making groups fire at each other as instructed by the event's parameters.
            # Start by iterating over the events.
            for event in self.side_b_timeline[self.time_pulse]:
                self.side_b.groups[event[0]].fire(self.side_a.groups[event[1]], event[2], event[3], event[4])
        # Update both sides.
        self.side_a.update()
        self.side_b.update()
        # Add each side's strength at the end of the pulse to the corresponding lists for plotting.
        self.side_a_staying_power.append(self.side_a.hit_points)
        self.side_b_staying_power.append(self.side_b.hit_points)
        # Advance the pulse counter by 1.
        self.time_pulse += 1

    def strength_plot(self):
        """Produce a chart of the relative fighting strengths of both sides during the battle."""
        sns.set_theme()
        self.battle_data.plot(y=['a_staying_power', 'b_staying_power'])
        plt.title(self.name, pad=15, fontweight='bold')
        plt.ylabel('Staying power', labelpad=5)
        plt.xlabel('Minute', labelpad=5)
        plt.legend(title="Belligerents", loc="lower left", labels=[self.side_a.name, self.side_b.name])
        chart = plt.gcf()
        if DRAW_PLOT:
            plt.show()
        if SAVE_PLOT:
            # Check whether the report directory exists, and create it if it does not.
            if not os.path.exists(self.report_path):
                os.makedirs(self.report_path)
            chart.savefig('{}{}.png'.format(self.report_path, self.name))

    def firepower_comparison(self, side_a_groups, side_b_groups):
        """Compare the firepower of specific groups of the belligerent sides at different distances.
        """

        # Determine the groups' maximum range.
        max_range = 0
        group_type = self.side_a.groups[side_a_groups[0]].group_type

        for group in side_a_groups:
            if self.side_a.groups[group].group_type != group_type:
                raise ValueError("Cannot compare firepower of groups of different types.")
            for ship in self.side_a.groups[group].members:
                if ship.main_armament_type.max_range > max_range:
                    max_range = ship.main_armament_type.max_range

        for group in side_b_groups:
            if self.side_b.groups[group].group_type != group_type:
                raise ValueError("Cannot compare firepower of groups of different types.")
            for ship in self.side_b.groups[group].members:
                if ship.main_armament_type.max_range > max_range:
                    max_range = ship.main_armament_type.max_range

        side_a_firepower = []
        side_b_firepower = []
        range_indices = []

        max_range = int((max_range // 1000) * 1000)

        for i in range(1000, max_range + 1000, 1000):
            range_indices.append(i)
            total_a_firepower_at_range = 0
            for group in side_a_groups:
                for ship in self.side_a.groups[group].members:
                    total_a_firepower_at_range += ship.return_firepower(i)
            side_a_firepower.append(total_a_firepower_at_range)

            total_b_firepower_at_range = 0
            for group in side_b_groups:
                for ship in self.side_b.groups[group].members:
                    total_b_firepower_at_range += ship.return_firepower(i)
            side_b_firepower.append(total_b_firepower_at_range)

        firepower_dict = {"range": range_indices, self.side_a.name: side_a_firepower,
                          self.side_b.name: side_b_firepower}
        firepower_dataframe = pd.DataFrame.from_dict(firepower_dict, dtype=float)
        firepower_dataframe.set_index("range")
        sns.set_theme()
        firepower_dataframe.plot(y=[1, 2])
        plt.title("Firepower comparison", pad=15, fontweight="bold")
        if group_type == "light":
            equivalent = 6
        else:
            equivalent = 15
        plt.ylabel("{}-inch hits".format(equivalent), labelpad=10)
        plt.xlabel("Range in Kyd", labelpad=10)
        plt.show()

    def export_battle_reports(self):
        # Check whether the report directory exists, and create it if it does not.
        if not os.path.exists(self.report_path):
            os.makedirs(self.report_path)

        # Save the side strength dataframe to a CSV file.
        strength_data_file_path = '{}{}_strength_report.csv'.format(self.report_path, self.battle_id_string)
        self.battle_data.to_csv(strength_data_file_path, header=True, index=False)

    def resolve(self):
        """Resolve the battle until there are no more events or one side is eliminated."""
        while self.time_pulse < (len(self.side_a_timeline)) \
                and self.side_a.hit_points > 0 and self.side_b.hit_points > 0:
            self.advance_pulse()
        # Join all the battle information into Pandas dataframes.
        starting_time = parse_battle_cfg(self.battle_id_string)['General']['time']
        time_stamp = datetime.datetime.strptime(starting_time, '%H:%M')
        time_stamps = [time_stamp.strftime('%H:%M')]
        for _ in range(self.time_pulse):
            time_stamp = time_stamp + datetime.timedelta(minutes=1)
            time_stamps.append(time_stamp.strftime('%H:%M'))
        self.battle_data = pd.DataFrame(
            {"time": time_stamps,
             "a_staying_power": self.side_a_staying_power,
             "b_staying_power": self.side_b_staying_power
             })

        # If the model is set to output battle reports to the console, print out the battle information and results.
        if CONSOLE_OUTPUT:
            battle_date = parse_battle_cfg(self.battle_id_string)["General"]["date"]
            print("{}, {}".format(self.name, battle_date))
            print(self.battle_data)
            print(self.side_a)
            print(self.side_b)
            print("Battle duration: {} minutes".format(self.time_pulse))

        # If the model is set to export battle reports to CSV, call the corresponding function.
        if REPORT:
            self.export_battle_reports()

        # If the model is set to either draw or save a plot, call the corresponding function.
        if DRAW_PLOT or SAVE_PLOT:
            self.strength_plot()


#################
# BATTLE LOADER #
#################

# The following function takes a battle ID string as its only input, and loads all of that battle's relevant parameters
# from its external data files. It then creates all the elements (guns, ships, groups, etc.) needed to resolve it, and
# returns a complete Battle object, ready for simulation.


def load_battle(battle_id_string):
    """Load all the information relevant to the battle specified by the input string, and return a working Battle object
    for simulation and analysis.
    """

    # LOAD GUN DATA

    # Build the gun dictionary.
    gun_table_dictionary = parse_gun_data("cocos")

    # Load fleet data.
    side_a_fleet_dictionary, side_b_fleet_dictionary = parse_fleet_lists(battle_id_string)

    # Load both side's group data
    side_a_group_dictionary, side_b_group_dictionary = parse_group_data(battle_id_string)

    # Make two dictionaries containing each side's Ship objects. Note that all Ship objects present in the battle are
    # created here, and they are unique. Any other mentions of ships (in group lists, fire methods etc.) in the program
    # simply refer to the Ship objects in these two dictionaries. If the user wants to duplicate a ship (in order to
    # create a new member of an existing class for example) they must make a new entry in the data files AND give it a
    # unique name. The reason this is handled this way is twofold: one, it makes intuitive sense, as real ships are
    # also unique; two, it allows the user to place the same Ship object in more than one group (so that it can, for
    # instance, fire as part of a column but receive fire individually). As only one instance of the ship exists,
    # damaging it in one part of the program will affect it in all other parts.

    # Initialise a list of the names of all the ships in side A.
    side_a_ship_roster = []
    # Iterate over side A's groups.
    for group in side_a_group_dictionary:
        for ship_name in side_a_group_dictionary[group][0]:
            # Avoid duplicates.
            if ship_name not in side_a_ship_roster:
                side_a_ship_roster.append(ship_name)

    # Initialise a list of the names of all the ships in side B.
    side_b_ship_roster = []
    # Iterate over side B's groups.
    for group in side_b_group_dictionary:
        for ship_name in side_b_group_dictionary[group][0]:
            # Avoid duplicates.
            if ship_name not in side_b_ship_roster:
                side_b_ship_roster.append(ship_name)

    # Initialise the ship dictionary for side A.
    side_a_ship_dictionary = {}

    # Populate it with unique Ship objects.
    for ship_name in side_a_ship_roster:
        name = side_a_fleet_dictionary[ship_name][0]
        hull_class = side_a_fleet_dictionary[ship_name][1]
        gun_table = side_a_fleet_dictionary[ship_name][13]
        gun_designation = side_a_fleet_dictionary[ship_name][14]
        main_armament_type = Gun(*gun_table_dictionary[gun_table][gun_designation])
        main_armament_count = int(side_a_fleet_dictionary[ship_name][15])
        main_armament_broadside = int(side_a_fleet_dictionary[ship_name][16])
        main_armament_bow = int(side_a_fleet_dictionary[ship_name][17])
        main_armament_stern = int(side_a_fleet_dictionary[ship_name][18])
        main_armament_end_arc = int(side_a_fleet_dictionary[ship_name][19])
        side_a_ship_dictionary[ship_name] = Ship(name, hull_class, main_armament_type, main_armament_count,
                                                 main_armament_broadside, main_armament_bow, main_armament_stern,
                                                 main_armament_end_arc)

    # Initialise the ship dictionary for side B.
    side_b_ship_dictionary = {}

    # Populate it with unique Ship objects.
    for ship_name in side_b_ship_roster:
        name = side_b_fleet_dictionary[ship_name][0]
        hull_class = side_b_fleet_dictionary[ship_name][1]
        gun_table = side_b_fleet_dictionary[ship_name][13]
        gun_designation = side_b_fleet_dictionary[ship_name][14]
        main_armament_type = Gun(*gun_table_dictionary[gun_table][gun_designation])
        main_armament_count = side_b_fleet_dictionary[ship_name][15]
        main_armament_broadside = side_b_fleet_dictionary[ship_name][16]
        main_armament_bow = int(side_b_fleet_dictionary[ship_name][17])
        main_armament_stern = int(side_b_fleet_dictionary[ship_name][18])
        main_armament_end_arc = int(side_b_fleet_dictionary[ship_name][19])
        side_b_ship_dictionary[ship_name] = Ship(name, hull_class, main_armament_type, main_armament_count,
                                                 main_armament_broadside, main_armament_bow, main_armament_stern,
                                                 main_armament_end_arc)

    # Create the two belligerent sides.
    # Begin with side A.
    # Set the name of the side from the config file.
    side_name = parse_battle_cfg("cocos")["Sides"]["side_a"]
    # Initialise and populate the group dictionary.
    side_a_groups = {}
    for group in side_a_group_dictionary:
        group_name = group
        group_members = [side_a_ship_dictionary[ship] for ship in side_a_group_dictionary[group][0]]
        group_type = side_a_group_dictionary[group][1]
        side_a_groups[group] = Group(group_name, group_members, group_type)

    # Create the Side object for side A.
    side_a = Side(side_name, side_a_groups)

    # Now with side B.
    # Set the name of the side from the config file.
    side_name = parse_battle_cfg("cocos")["Sides"]["side_b"]
    # Initialise and populate the group dictionary.
    side_b_groups = {}
    for group in side_b_group_dictionary:
        group_name = group
        group_members = [side_b_ship_dictionary[ship] for ship in side_b_group_dictionary[group][0]]
        group_type = side_b_group_dictionary[group][1]
        side_b_groups[group] = Group(group_name, group_members, group_type)

    # Create the Side object for side B.
    side_b = Side(side_name, side_b_groups)

    # Register the fire events.
    side_a_events, side_b_events = parse_battle_events(battle_id_string)
    for event in side_a_events:
        side_a.register_fire_event(*event)
    for event in side_b_events:
        side_b.register_fire_event(*event)

    # Create the Battle object and return it.
    battle_name = parse_battle_cfg(battle_id_string)["General"]["name"]
    battle = Battle(battle_id_string, battle_name, side_a, side_b)

    return battle


cocos = load_battle("cocos")
cocos.resolve()
print(cocos.side_a.groups["Sydney"].members[0].hits_received)
cocos.firepower_comparison(["Sydney"], ["Emden"])
