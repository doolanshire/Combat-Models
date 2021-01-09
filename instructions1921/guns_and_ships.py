import csv
from math import e
import plot


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

    Methods:
        - return_to_hit(target_range): returns the base number of hits per gun per minute at the range provided.
        - return_damage_conversion_factor(): the 1921 Royal Navy rules convert all hits to two standard calibres:
        6-inch hits for light ships, and 15-inch hits for battlecruisers and battleships. This method returns the factor
        needed to convert a gun's hits to the equivalent 6-inch or 15-inch hits
        - return_equivalent_damage(target_range): returns the return_to_hit() number multiplied by the conversion
        factor. Essentially combines the two methods above into one.
    """

    def __init__(self, name, mount, caliber, max_range, long_to_hit, long_min, effective_to_hit, effective_min,
                 short_to_hit):
        self.name = name
        self.mount = mount
        self.caliber = max(0, caliber)
        self.max_range = max_range
        self.long_to_hit = long_to_hit
        self.long_min = long_min
        self.effective_to_hit = effective_to_hit
        self.effective_min = effective_min
        self.short_to_hit = short_to_hit
        self.active = True

    def return_to_hit(self, target_range):
        """Return the chance to hit (per gun and minute) for a given range. If the target is out of range, return 0."""
        if target_range > self.max_range:
            return 0
        elif target_range > self.long_min:
            return self.long_to_hit
        elif target_range > self.effective_min:
            return self.effective_to_hit
        elif target_range >= 0:
            return self.short_to_hit
        else:
            raise ValueError("Range must be a positive integer")

    def return_damage_conversion_factor(self):
        """The 1921 Royal Navy rules convert all hits to an equivalent number of 6-inch hits (light guns) or 15-inch
        hits (heavy guns). This function returns the factor needed for the conversion.
        """
        # Conversion factor to 6-inch hits for light gun calibers
        if self.caliber <= 9.5:
            # The conversion factors below are as stated in the original 1921 rules
            if self.caliber == 4:
                damage_equivalent = 1/3
            elif self.caliber == 4.7:
                damage_equivalent = 1/2
            elif self.caliber == 6:
                damage_equivalent = 1
            elif self.caliber == 7.5:
                damage_equivalent = 3
            # All other light calibers are determined through interpolation
            # We used exponential regression (R squared value of 0.9941)
            else:
                damage_equivalent = 1 / (37.523 * (e**(-0.622 * self.caliber)))
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

    def __init__(self, name, hull_class, main_armament_type, main_armament_count, main_armament_broadside):
        self.name = name
        self.hull_class = hull_class
        self.main_armament_type = main_armament_type
        self.main_armament_count = main_armament_count
        self.main_armament_broadside = main_armament_broadside
        self.staying_power = main_armament_count
        # Calculate the staying power multiplier for battleships based on main gun calibre.
        if self.hull_class == "battleship":
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
        elif self.hull_class == "battle cruiser":
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
        elif self.hull_class == "light cruiser":
            if self.main_armament_type.caliber <= 4:
                self.staying_power *= 4
            elif self.main_armament_type.caliber <= 6:
                self.staying_power *= 8
            else:
                self.staying_power *= 9
            # Set the minimum caliber of the gun that can damage a battleship.
            self.minimum_to_damage = 4
        # Calculate the staying power multiplier for light squadron ships based on main gun calibre.
        elif self.hull_class in ("flotilla leader", "destroyer"):
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

    def fire(self, target, target_range, distribution=1, salvo_size=None, modifier=1):
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
        # Unless otherwise specified, the ship is assumed to fire a full broadside
        if salvo_size is None:
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

    def __init__(self, name, members):
        self.name = name
        self.members = members
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
        - name: the group's name (string).
        - groups: the ship groups belonging to the side (list).
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
        self.staying_power = sum(group.staying_power for group in groups)
        self.hit_points = self.starting_hit_points = self.staying_power
        self.status = 1
        self.fire_events = []
        self.latest_event = 0

    def update(self):
        """Applies pending damage to all groups in the side, and updates hit points and status accordingly.
        This method is run once every time pulse.
        """
        for group in self.groups:
            group.update()
        self.hit_points = sum(group.hit_points for group in self.groups)
        self.status = self.hit_points / self.staying_power

    def register_fire_event(self, firer, target, target_range, start, duration, salvo_size=None, modifier=1):
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
        new_event = (firer, target, target_range, start, start + duration, salvo_size, modifier)

        # Append the tuple to the list of fire events for the side
        self.fire_events.append(new_event)

    def __str__(self):
        group_names = [group.name for group in self.groups]
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
        - a_plot: a list containing the total hit points of side A at each minute of the action, so that a graph can
        be plotted at the end of the battle (list).
        - b_plot: same as above, but for side B (list).
        - time_pulse: the current minute of the battle. Begins at 0 and is advanced by 1 every time the advance_pulse()
        method is called (integer).

    Methods:
        - advance_pulse(): advances the battle by one minute. This method executes all the fire events pending for the
        current minute, assigning damage to both sides. At the end of the time pulse all pending damage is applied, the
        lists a_plot and b_plot are updated, and the status of all ships in both sides is refreshed. The variable
        time_pulse is also increased by one.
        - resolve(): automatically resolves the entire battle, pulse by pulse, until either side is out of action or
        all fire events have been executed.
    """

    def __init__(self, name, side_a, side_b):
        self.name = name
        self.side_a = side_a
        self.side_b = side_b
        # Determine the battle duration.
        battle_duration = max(self.side_a.latest_event, self.side_b.latest_event)
        # Initialise fire event timelines for both sides.
        self.side_a_timeline = [[] for _ in range(battle_duration)]
        self.side_b_timeline = [[] for _ in range(battle_duration)]
        # Initialise the strength plot for both sides.
        self.a_plot = [self.side_a.staying_power]
        self.b_plot = [self.side_b.staying_power]
        # Set the current time pulse to 0.
        self.time_pulse = 0

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
                    # Add to each minute a tuple containing the firer, target, range, salvo size and fire modifier
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
        self.a_plot.append(self.side_a.hit_points)
        self.b_plot.append(self.side_b.hit_points)
        # Advance the pulse counter by 1.
        self.time_pulse += 1

    def resolve(self):
        """Resolve the battle until there are no more events or one side is eliminated"""
        while self.time_pulse < (len(self.side_a_timeline)) \
                and self.side_a.hit_points > 0 and self.side_b.hit_points > 0:
            self.advance_pulse()


def build_gun_dictionary(filename):
    """Build a dictionary of gun parameters from an external CSV file:
        - Key: the gun designation (e.g. '13.5 in V' or '12 in XI')
        - Value: a list of parameters, in the order:
            * caliber (in inches)
            * max_ange (maximum range in yards)
            * long_to_hit (chance to hit per gun and minute at long range)
            * long_min (minimum range considered to be long)
            * effective_to_hit (chance to hit per gun and minute at effective range)
            * effective_min (minimum range considered to be effective)
            * short_to_hit (chance to hit per gun and minute at short range)
    """

    gun_dict = {}
    with open(filename) as sourcefile:
        reader = csv.reader(sourcefile, delimiter=",")
        next(reader)
        for row in reader:
            gun_data = list(row)
            gun_dictionary_entry = gun_data[:2]
            gun_dictionary_entry += list(map(float, gun_data[2:]))
            gun_dict[gun_data[0]] = gun_dictionary_entry
    return gun_dict


# Build the gun dictionary for capital ships
capital_guns = build_gun_dictionary("capital_ship_guns.csv")

# Build the gun dictionary for cruisers
cruiser_guns = build_gun_dictionary("light_cruiser_guns.csv")

# Build the gun dictionary for destroyers
destroyer_guns = build_gun_dictionary("destroyer_guns.csv")

# Build the gun dictionary for destroyers
secondary_guns = build_gun_dictionary("secondary_guns.csv")

# CREATE TEST SHIPS
print("SHIP CREATION TESTS")
emden = Ship("SMS Emden", "light cruiser", Gun(*destroyer_guns["4 in V"]), 10, 5)
emden.main_armament_type.caliber = 4.1
print("* Ship information *")
print(emden)
sydney = Ship("HMAS Sydney", "light cruiser", Gun(*cruiser_guns["6 in XII"]), 8, 5)
print(sydney)

# CREATE TEST GROUPS
print("GROUP CREATION TESTS")
print("* Group information *")
german_one = Group("SMS Emden", [emden])
print(german_one)
british_one = Group("HMAS Sydney", [sydney])
print(british_one)

# Test side creation
print("* Creating German side *")
germany = Side("Germany", [german_one])
print(germany)
print("* Creating a British side *")
britain = Side("Britain", [british_one])
print(britain)

# Test fire event registration
# Both sides fire at 9000 yards for 5 minutes, then at 8000 yards for 4 minutes, then 7000 for 12.
germany.register_fire_event(0, 0, 9000, 0, 5, None, 1)
britain.register_fire_event(0, 0, 9000, 0, 5, None, 1)
germany.register_fire_event(0, 0, 8000, 5, 4, None, 1)
britain.register_fire_event(0, 0, 8000, 5, 4, None, 1)
germany.register_fire_event(0, 0, 7000, 9, 12, None, 1)
britain.register_fire_event(0, 0, 7000, 9, 12, None, 1)
print(germany.fire_events)
print(britain.fire_events)

# Test battle creation
print("* Creating a test battle *")
ross_island = Battle("Ross Island", germany, britain)
print(ross_island.side_a_timeline)
print(ross_island.side_b_timeline)

ross_island.resolve()

plot.strength_plot(ross_island.a_plot, "Germany", ross_island.b_plot, "Britain")
