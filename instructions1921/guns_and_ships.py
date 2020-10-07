import csv


class Gun:
    """
    A naval gun, as mounted on a ship.

    Attributes:
        - caliber: the caliber of the gun in inches.
        - max_range: maximum range in yards.
        - long_to_hit: chance to hit per gun per minute at long range.
        - long_min: minimum range in yards considered to be long range.
        - effective_to_hit: chance to hit per gun per minute at effective range.
        - effective_min: minimum range in yards considered to be effective.
        - short_to_hit: chance to hit per gun per minute at short range.
        - active: whether the gun is active (True) or Out Of Action (False). All guns are initialised as active.
    """

    def __init__(self, caliber, max_range, long_to_hit, long_min, effective_to_hit, effective_min, short_to_hit):
        self.caliber = caliber
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

    def is_active(self):
        """Return True if the gun is active, False if it is Out Of Action."""
        return self.active

    def knock_out(self):
        """Knock the gun out (make it inactive). Caused by enemy fire."""
        self.active = False

class Ship:
    """
    A ship, treated as an armoured weapons platform.

    Attributes:
        - name: the name of the ship.
        - date: the date of completion.
        - speed: the full speed of the ship in knots.
        - capital: the ship's capital guns. A list of Gun objects. Starts as empty upon object initialisation,
        and is later populated by the add_capital_guns() method.
        - cruiser: the ship's cruiser guns. A list of Gun objects. Starts as empty upon object initialisation,
        and is later populated by the add_cruiser_guns() method.
        - destroyer: the ship's destroyer guns. A list of Gun objects. Starts as empty upon object initialisation,
        and is later populated by the add_destroyer_guns() method.
        -
    """


def build_gun_dictionary(filename):
    """Build a dictionary of gun parameters from an external CSV file:
        - Key: the gun designation (e.g. '13.5 in V' or '12 in XI')
        - Value: a list of parameters, in the order:
            * caliber (in inches)
            * maxrange (maximum range in yards)
            * longtohit (chance to hit per gun and minute at long range)
            * longmin (minimum range considered to be long)
            * effectivetohit (chance to hit per gun and minute at effective range)
            * effectivemin (minimum range considered to be effective)
            * shorttohit (chance to hit per gun and minute at short range)
    """

    gun_dict = {}
    with open(filename) as sourcefile:
        reader = csv.reader(sourcefile, delimiter=",")
        next(reader)
        for row in reader:
            gun_data = list(row)
            gun_dict[gun_data[0]] = list(map(float, gun_data[1:]))
    return gun_dict

# Build the gun dictionary for capital ships
capital_guns = build_gun_dictionary("capital_ship_guns.csv")

# Build the gun dictionary for cruisers
cruiser_guns = build_gun_dictionary("light_cruiser_guns.csv")

# Build the gun dictionary for destroyers
destroyer_guns = build_gun_dictionary("destroyer_guns.csv")

# Build the gun dictionary for destroyers
secondary_guns = build_gun_dictionary("secondary_guns.csv")

# TEST FOR GUN CREATION AND ONE METHOD #
# Create the gun from the dictionary by its designation
new_gun = Gun(*capital_guns["13.5 in V"])
# Print the chance to hit at the range specified
print(new_gun.return_to_hit(23000))
