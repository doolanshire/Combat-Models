#########################################
# NAVAL WAR COLLEGE MANEUVER RULES 1922 #
#########################################

# import math
import os
import pandas as pd
import random


FIRE_EFFECT_TABLES_EDITION = "1930"


class Gun:
    """A naval gun. All parameters are loaded from external data files upon object creation.

    The following Class variables exist, containing information relevant to all Gun instances:
    - general_data (DataFrame): a table listing the caliber, projectile weight, muzzle velocity and maximum range of all
    gun denominations, as well as the navies in which they saw service.
    - penetrative_values (DataFrame): a table listing the multipliers needed to convert penetrative hits from every
    caliber to equivalent 14-inch hits.
    - non_penetrative_values (DataFrame): a table listing the multipliers needed to convert non-penetrative hits from
    every caliber to equivalent 14-inch hits.
    - rate_of_fire (DataFrame): a table listing the rates of fire of all gun designations at all ranges (in 1000-yard
    increments).

    Instance variables are documented in the constructor method docstring.
    """

    # GUN TYPES
    # Load the CSV file containing general data for all gun designations.
    gun_types_path = "fire_effect_tables/{}/gun_types.csv".format(FIRE_EFFECT_TABLES_EDITION)
    general_data = pd.read_csv(gun_types_path, index_col="designation", na_values="--")

    # HIT VALUE CONVERSION FACTORS
    # Define the paths for the hit value tables.
    penetrative_path = "fire_effect_tables/{}/hit_values_penetrative.csv".format(FIRE_EFFECT_TABLES_EDITION)
    non_penetrative_path = "fire_effect_tables/{}/hit_values_non_penetrative.csv".format(FIRE_EFFECT_TABLES_EDITION)
    # Load the data.
    penetrative_values = pd.read_csv(penetrative_path, index_col="caliber", dtype=float)
    non_penetrative_values = pd.read_csv(non_penetrative_path, index_col="caliber", dtype=float)

    # RATE OF FIRE
    # Define the path for the rates of fire table.
    rates_of_fire_path = "fire_effect_tables/{}/rates_of_fire.csv".format(FIRE_EFFECT_TABLES_EDITION)
    # Create a rate of fire dataframe.
    rate_of_fire = pd.read_csv(rates_of_fire_path, index_col='range', na_values="--", dtype=float)

    def __init__(self, gun_designation):
        """All parameters for each individual gun are loaded from external CSV files and calculated upon creation of
        each instance. The only necessary parameter to create a gun is its designation, following the format:

        [caliber]-in-[length]

        For example, '6-in-50' means the 6-inch/50 gun.
         
        Guns in AA mounts append '-A' to the designation (e.g. '4-in-45-A' is the 4-inch/45 AA gun).
         
        Parameters:
            - gun_designation (string): the text string of the gun's designation as described above.
             
        Attributes:
            - caliber (float): the gun's caliber in inches.
            - projectile_weight (float): the projectile weight in lbs.
            - muzzle_velocity (int): the muzzle velocity in feet per second.
            - maximum_range (int): the gun's maximum range in thousands of yards.
            - hit_percentage (dict): a dictionary of Pandas DataFrames listing the gun's hit percentages at different
              firing ranges (in 1000-yard intervals) and for different target sizes ("large", "intermediate", "small",
              "destroyer" and "submarine". The dictionary keys are the different spot types ("top", "kite" and "plane").
              Note that only the 1922 revision of the rules uses kite spot.
            - side_penetration_ranges (DataFrame): a table listing the range limits for side (belt) penetration of
              various armor thicknesses.
            - deck_penetration_ranges (DataFrame): a table listing the range limits for deck penetration of various
              armor thicknesses. Only applies to guns 5.5 inches in caliber or greater.
        """

        self.designation = gun_designation
        # Define the path for the gun's fire effect tables
        fire_effect_tables_path = "fire_effect_tables/{}/{}/".format(FIRE_EFFECT_TABLES_EDITION, gun_designation)

        # GENERAL DATA

        self.caliber = float(self.designation.split("-")[0])

        # Fill out the gun's general data.
        self.projectile_weight = int(Gun.general_data["projectile_weight"][self.designation])
        self.muzzle_velocity = int(Gun.general_data["muzzle_velocity"][self.designation])
        self.maximum_range = int(Gun.general_data["maximum_range"][self.designation])

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

        # armor PENETRATION

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
        """Returns the hit percentage of the gun for a given target size, range and spot type.
        
        Parameters:
            - target_size (string): the size of the target ("large", "intermediate", "small", "destroyer" or
              "submarine").
            - target_range (int): the range to the target in thousands of yards.
            - spot_type (string): the type of spot used ("top", "plane" or "kite").
            
        Returns: the hit percentage (float).
        """
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
        """Returns the rate of fire for the gun at a given range.
        
        Parameters:
            - target_range (int): the range to the target in thousands of yards.
            
        Returns: the rate of fire at the range given (float).
        """
        if target_range > self.maximum_range:
            return 0
        else:
            return Gun.rate_of_fire[self.designation][target_range]

    def return_hit_value(self, target_size, penetrative):
        """Returns the multiplier needed to convert a hit from the gun to the 14-inch hit equivalent.
        
        Attributes:
            - penetrative (boolean): whether the hit is penetrative or not.
        
        Returns: the conversion factor (float).    
        """
        
        if penetrative:
            if target_size == "submarine":
                return Gun.penetrative_values[target_size][self.caliber]
            else:
                return Gun.penetrative_values["large, intermediate, small, destroyer"][self.caliber]

        else:
            return Gun.non_penetrative_values[target_size][self.caliber]

    def return_side_penetration(self, armor, deflection, target_range):
        """Returns whether the gun would penetrate the side (belt) armor of a target.
        
        Parameters:
            - armor (float): the target's side armor in inches.
            - deflection (int): the shot deflection in degrees. Converted to 15-degree increments within the method.
            - target_range (int): the range to the target in thousands of yards.
            
        Returns: True if the shot penetrates, False if it does not.
        """
        
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
        """Returns whether the gun would penetrate the deck armor of a target.
        
        Attributes:
            - armor (float): the target's deck armor in inches.
            - target_range (int): the range to the target in thousands of yards.
        """
        
        # Deck penetration only applies to guns 5.5 inches or larger.
        if self.caliber < 5.5:
            return False

        else:
            armor_values = self.deck_penetration_ranges.index
            # Return false if the armor is thicker than what is listed in the penetration tables.
            if armor > max(armor_values):
                return False
            # Likewise, return True if the armor is thinner than the minimum value listed.
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


class Battery:
    """A battery of guns of the same caliber. Batteries are defined by their gun designation and caliber, the type of
    battery (primary, secondary or tertiary), the total number of mounts on the ship and their type (turret, casemate),
    the number of guns per mount, whether the battery has a low freeboard, and the number of mounts bearing on each arc
    (bow, broadside or stern) as well as the angle from the bow and stern defining those arcs.
    """

    def __init__(self, gun_type, battery_type, mount_type, total_mounts, bow_mounts, broadside_mounts, stern_mounts,
                 end_arc, guns_per_mount, low_freeboard=False):
        """All parameters are loaded automatically from external files (in particular from the fleet lists).

        Parameters:
            - gun_type (Gun object): a Gun object of the type used in the battery.
            - battery_type (string): "primary", "secondary" or "tertiary". Fire events decide which guns are firing
              according to these categories. Note that ships having guns of the same caliber in different mount types
              (for example the 1906 Scharnhorst class, with four 8.3-inch guns in two centerline turrets and another
              four in broadside casemates) can have more than one battery of the same type (in this case, two different
              primary batteries in different mounts).
            - mount_type (string): "turret" or "casemate". May affect rate of fire in some versions of the rules.
            - total_mounts (int): the total number of mounts present in the battery.
            - bow_mounts (int): the number of mounts bearing on the bow arc.
            - broadside_mounts (int): the number of mounts bearing on the broadside arc.
            - stern_mounts (int): the number of mounts bearing on the stern arc.
            - end_arc (int): the angle (in degrees) from the bow or stern at which the firing arc changes.
            - guns_per_mount (int): the number of guns per mount.
            - low_freeboard (bool): whether the guns are considered to be mounted low and close to the waterline. Guns
              thus mounted cannot fire in rough seas. Defaults to 'False'.

        Attributes:
            - caliber (float): the battery's caliber, extracted from the gun type.
        """
        self.gun_type = gun_type
        self.caliber = gun_type.caliber
        self.battery_type = battery_type
        self.mount_type = mount_type
        self.total_mounts = total_mounts
        self.bow_mounts = bow_mounts
        self.broadside_mounts = broadside_mounts
        self.stern_mounts = stern_mounts
        self.end_arc = end_arc
        self.guns_per_mount = guns_per_mount
        self.low_freeboard = low_freeboard


class Ship:
    """A naval ship. All the data needed to instantiate a new Ship object can be found in the corresponding fleet list
    data files.
    """

    def __init__(self, name, hull_class, size, life, side, deck, primary_fire_effect_table, primary_total,
                 primary_broadside, primary_bow, primary_stern, primary_mount, primary_end_arc,
                 secondary_fire_effect_table, secondary_total, secondary_broadside, secondary_bow, secondary_stern,
                 secondary_mount, secondary_end_arc, torpedoes_type, torpedoes_mount, torpedoes_total, torpedoes_side):
        """Parameters:

            *General*
            - name (string): the name of the ship.
            - hull class (string): BB, CC, CA, CL, DD, etc. For a list of all possible values check the file
              'life_coefficients' in the 'helper_functions/' directory.
            - size (string): large, intermediate, small, destroyer or submarine.
            - side (float): the side (belt) armor amidships, in inches.
            - deck (float): the deck armor amidships, in inches.

            *Primary armament*
            - primary_fire_effect_table (string): the fire effect table used by the primary armament (e.g. "6-in-50").
            - primary_total (int): the number of turrets in the main battery.
            - primary_broadside (int): the number of turrets the ship can fire broadside-on.
            - primary_bow (int): the number of turrets the ship can fire at a target ahead.
            - primary_stern (int): the number of turrets the ship can fire at a target astern.
            - primary_mount (int): the number of guns per turret in the ship's primary armament.
            - primary_end_arc (int): the number of degrees from the bow or stern before the firing arc is considered to
            be broadside-on.

            *Secondary armament*
            As above, except with secondary_ as a prefix.

            *Torpedoes*
            - torpedoes_type (string): the type and caliber of the torpedoes carried by the ship, if any.
            - torpedoes_mount (string): whether the torpedo tubes are submerged (S) or deck-mounted (D).
            - torpedoes_total (int): total number of torpedo tubes.
            - torpedoes_side (int): number of torpedo tubes which can fire on either side.

        Attributes:
            *Life*
            - hit_points (float): starts with the same value as the 'life' parameter and gets reduced by damage.
            - starting_hit_points (float): starts with the same value as the 'hit_points' attribute above, but
              represents the ship's hit points at the start of a three-minute move. At the end of the move, and after
              all gunnery damage has been subtracted from the 'hit_points' attribute, 'starting_hit_points' is updated
              with the value of the attribute 'hit_points'.
            - status (fraction): the total fraction remaining of the ship's life. Defined as the ship's hit points
              divided by its original life value. It affects gunnery, and is updated at the end of every move.

            *Motion*
            - initial_speed / current_speed (float): the speed in knots at the end of the last move, and at the start
              of the current move. Used to track ship acceleration and deceleration as it affects gunnery.
            - initial_course / current_course (int): the ship's course at the end of the last move, and at the start of
              the current move. Used to track changes of course (of firing and target ships) which may affect gunnery.

            *Targeting*
            - previous_target_data / target_data (DataFrames): tables containing the relevant data of all of the ship's
              targets, used to calculate fire corrections. Upon initialisation these DataFrames are empty, and they are
              populated through the Ship.target() method.
        """

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
        self.primary_mount = primary_mount
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
        self.secondary_mount = secondary_mount
        self.secondary_end_arc = secondary_end_arc
        # Torpedo tubes might be implemented in the future.
        self.torpedoes_type = torpedoes_type
        self.torpedoes_mount = torpedoes_mount
        self.torpedoes_total = torpedoes_total
        self.torpedoes_side = torpedoes_side

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

    def calculate_turret_arc(self, target_bearing):
        """Return the turret arc the target lies on.

        Parameters:
            - target_bearing (int): the target bearing in degrees.

        Returns: a string ("broadside", "bow" or "stern") indicating the firing arc.
        """

        if target_bearing > 180:
            target_bearing = 180 - (target_bearing % 180)
        if target_bearing < self.primary_end_arc:
            return "bow"
        elif target_bearing > (180 - self.primary_end_arc):
            return "stern"
        else:
            return "broadside"

    def calculate_turrets_bearing(self, turret_arc):
        """Return the number of turrets bearing on a given arc.

        Parameters:
            - turret_arc (string): "broadside", "bow" or "stern".

        Returns: the number of turrets bearing on the specified arc (int).
        """

        if turret_arc == "bow":
            return self.primary_bow
        elif turret_arc == "stern":
            return self.primary_stern
        else:
            return self.primary_broadside

    def calculate_primary_salvo_size(self, turret_arc):
        """Calculates the number of guns bearing on a target based on the firing arc.

        Parameters:
            - target_bearing: the target bearing in degrees. Any input larger than 180 is converted to the 0-180 range.

        Returns: an integer representing the number of guns that can fire at a target at the input bearing.
        """

        turrets_bearing = self.calculate_turrets_bearing(turret_arc)
        return turrets_bearing * self.primary_mount

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

        Returns: the expected base number of hits (float).
        """

        turrets_bearing = self.calculate_turret_arc(target_bearing)
        salvo_size = self.calculate_primary_salvo_size(turrets_bearing)
        rate_of_fire = self.primary_armament.return_rate_of_fire(target_range)
        base_to_hit = self.primary_armament.return_hit_percentage(target_size, target_range, spot_type)
        base_hits = salvo_size * rate_of_fire * base_to_hit

        return base_hits

    def target(self, firing_side, firing_group, target_group, target_ships, fire, target_range, target_bearing, evasive,
               target_deflection):
        """Add a target to the ship's target_list DataFrame. Additionally, register the firing ship in the target's
        'taking_fire_from' DataFrame. Eventually this will be done automatically from a battle's fire events CSV files.

        Parameters:
            - firing_side (string): either "side_a" or "side_b". The method will look for the firing group in the
              corresponding side's group dictionary.
            - firing_group (string): the name of the firing group.
            - target_group (string): the name of the group being targeted.
            - target_ships (list): the names of the ships being targeted. A single target will be a list of length one.
            - fire (boolean): whether the target is being fired at (True) or just tracked (False).
            - target_range (int): the range to the target in thousands of yards.
            - target_bearing (int): the target bearing in degrees.
            - evasive (boolean): whether the target is doing evasive maneuvers, defined as turning to both sides within
              the duration of one move (three minutes).
            - target_deflection (int): the shot deflection in degrees, used to determine whether the shots would be
              penetrating.
        """
        target_list = []
        if firing_side == "side_a":
            for ship in target_ships:
                target_list.append(side_b.groups[target_group].ships[ship])

        elif firing_side == "side_b":
            for ship in target_ships:
                target_list.append(side_a.groups[target_group].ships[ship])

        for ship in target_list:
            turret_arc = self.calculate_turret_arc(target_bearing)
            penetration = self.primary_armament.return_side_penetration(ship.side, target_deflection, target_range)
            self.target_data.loc[ship.name] = (firing_group, target_group, ship.name, fire, 0, turret_arc,
                                               target_range, evasive, target_deflection, penetration)

    def allocate_primary_turrets(self):
        """Distribute the available primary turrets among the targets in the ship's target_data. The criteria followed:

        * If the bow or stern arcs are engaged, these take one turret away from the broadside arc.
        * In a first pass, the turrets are distributed uniformly among the targets using integer division. For example,
        distributing 7 turrets among 5 targets, the method will allocate 7 // 5 = 1 turret per target, with a remainder
        of two. Note how, should there be more targets than turrets, this first pass will assign 0 turrets per target.
        * Any turrets remaining are allocated one by one to the targets in the order they were targeted, until no more
        turrets are left.
        """
        target_bearings = self.target_data['target_bearing'].tolist()
        bow_targets = stern_targets = 0
        # Check whether the bow arc is engaged.
        remaining_bow_turrets = remaining_stern_turrets = remaining_broadside_turrets = 0

        if "bow" in target_bearings:
            bow_turrets = self.primary_bow
            bow_targets = self.target_data['target_bearing'].value_counts()['bow']
            bow_turrets_per_target = bow_turrets // bow_targets
            remaining_bow_turrets = bow_turrets % bow_targets
            self.target_data.loc[(self.target_data['fire']) &
                                 (self.target_data['target_bearing'] == "bow"),
                                 "allocated_turrets"] = bow_turrets_per_target

        # Check whether the stern arc is engaged.
        if "stern" in target_bearings:
            stern_turrets = self.primary_stern
            stern_targets = self.target_data['target_bearing'].value_counts()['stern']
            # Allocate turrets to all targets in a stern arc.
            stern_turrets_per_target = stern_turrets // stern_targets
            remaining_stern_turrets = stern_turrets % stern_targets
            self.target_data.loc[(self.target_data['fire']) &
                                 (self.target_data['target_bearing'] == "stern"),
                                 "allocated_turrets"] = stern_turrets_per_target

        # Check whether the broadside is engaged. Remove one turret from it if either bow or stern are engaged, two
        # if both are engaged.
        if "broadside" in target_bearings:
            broadside_turrets = self.primary_broadside
            if bow_targets > 0:
                broadside_turrets -= 1
            if stern_targets > 0:
                broadside_turrets -= 1
            broadside_targets = self.target_data['target_bearing'].value_counts()['broadside']
            # Allocate turrets to all targets in a broadside arc.
            broadside_turrets_per_target = broadside_turrets // broadside_targets
            remaining_broadside_turrets = broadside_turrets % broadside_targets
            self.target_data.loc[(self.target_data['fire']) &
                                 (self.target_data['target_bearing'] == "broadside"),
                                 "allocated_turrets"] = broadside_turrets_per_target

        # Iterate over the dataframe allocating the remaining turrets.
        for i, row in self.target_data.loc[self.target_data['fire']].iterrows():
            if row['target_bearing'] == "bow" and remaining_bow_turrets > 0:
                self.target_data.at[i, 'allocated_turrets'] += 1
                remaining_bow_turrets -= 1
            if row['target_bearing'] == "stern" and remaining_stern_turrets > 0:
                self.target_data.at[i, 'allocated_turrets'] += 1
                remaining_stern_turrets -= 1
            if row['target_bearing'] == "broadside" and remaining_broadside_turrets > 0:
                self.target_data.at[i, 'allocated_turrets'] += 1
                remaining_broadside_turrets -= 1

    def return_first_correction(self, target):
        """Returns the first correction to gunfire – a ratio which reduces rate of fire. It begins at a value of 1
        (no reduction) and diminishes in steps of one tenth depending on circumstances affecting gunnery. The factors
        taken into account are:

        * Ship status: a ship that has suffered damage will have its rate of fire reduced by the same proportion.
        * If opening fire, either because the target had not been fired at before, or because fire had been interrupted
        for three minutes or longer, a penalty is applied ranging between two tenths (20% reduction) and unity (no fire
        possible) depending on the range to the target.
        * If fire is shifted to a target in close formation with the previous one (and if the above rule does not apply)
        rate of fire is reduced by a flat three tenths.

        Returns: the first correction as a ratio (0 to 1) applied to rate of fire.
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
                # opening_fire = True
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
sydney = Ship("Sydney", "CL", "small", 3.17, 3, 2, "6-in-50", 8, 4, 2, 2, 1, 45, "NA", "NA", "NA", "NA", "NA", "NA",
              "NA", "B 21 in", "S", 2, 2)
brisbane = Ship("Brisbane", "CL", "small", 3.17, 3, 2, "6-in-50", 8, 4, 2, 2, 1, 45, "NA", "NA", "NA", "NA", "NA", "NA",
                "NA", "B 21 in", "S", 2, 2)
melbourne = Ship("Melbourne", "CL", "small", 3.17, 3, 2, "6-in-50", 8, 4, 2, 2, 1, 45, "NA", "NA", "NA", "NA", "NA",
                 "NA", "NA", "B 21 in", "S", 2, 2)

# Test ship motion data
sydney.initial_speed = brisbane.initial_speed = melbourne.initial_speed = 12
sydney.current_speed = brisbane.current_speed = melbourne.current_speed = 14
sydney.initial_course = brisbane.initial_course = melbourne.initial_course = 90
sydney.current_course = brisbane.current_course = melbourne.current_course = 120

# Test ships (Germany
emden = Ship("Emden", "CL", "small", 2.37, 3, 1.2, "4-in-45-A", 10, 5, 2, 2, 1, 30, "NA", "NA", "NA", "NA", "NA", "NA",
             "NA", "B 17.7 in", "S", 2, 2)
dresden = Ship("Dresden", "CL", "small", 2.37, 3, 1.2, "4-in-45-A", 10, 5, 2, 2, 1, 30, "NA", "NA", "NA", "NA", "NA",
               "NA", "NA", "B 17.7 in", "S", 2, 2)

# Test ship motion data
emden.initial_speed = dresden.initial_speed = 10
emden.current_speed = dresden.current_speed = 15
emden.initial_course = dresden.initial_course = 80
emden.current_course = dresden.current_course = 90

# Test ship dictionary
ship_dictionary = {"Sydney": sydney, "Melbourne": melbourne, "Brisbane": brisbane, "Emden": emden, "Dresden": dresden}

# Test group ship dictionaries
side_a_group_ships = {"Sydney": sydney, "Brisbane": brisbane, "Melbourne": melbourne}
side_b_group_ships = {"Emden": emden, "Dresden": dresden}

# Test groups
side_a_groups = {"Brisbane, Sydney and Melbourne": Group("Brisbane, Sydney and Melbourne", side_a_group_ships, False)}
side_b_groups = {"Emden and Dresden": Group("Emden and Dresden", side_b_group_ships, True)}

# Test sides
side_a = Side("Australia", side_a_groups)
side_b = Side("Germany", side_b_groups)

# Test gun
test_gun = Gun("6-in-50")

# Target Sydney as Emden
emden.target("side_b", "Emden and Dresden", "Brisbane, Sydney and Melbourne", ["Brisbane"], False, 12, 85, True, 90)
# Advance one turn
emden.previous_target_data = emden.target_data.copy()
# Target again, firing this time
emden.target("side_b", "Emden and Dresden", "Brisbane, Sydney and Melbourne", ["Brisbane"], True, 10, 70, True, 75)
emden.target("side_b", "Emden and Dresden", "Brisbane, Sydney and Melbourne", ["Sydney"], True, 10, 70, True, 75)

emden.target("side_b", "Emden and Dresden", "Brisbane, Sydney and Melbourne", ["Melbourne"], True, 10, 70, True, 75)

# Check range rate on target
range_rate = abs(emden.target_data["target_range"]["Brisbane"] - emden.previous_target_data["target_range"]["Brisbane"])
print(range_rate)

# Print target data
print(emden.return_first_correction("Brisbane"))
emden.allocate_primary_turrets()

with pd.option_context('display.max_rows', 5, 'display.max_columns', None, 'display.width', None):
    print(emden.previous_target_data)
    print(emden.target_data)
