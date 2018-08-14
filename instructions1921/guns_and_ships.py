import csv


class Gun:
    """
    A naval gun, as mounted on a ship.

    Attributes:
        - caliber: the caliber of the gun in inches.
        - maxrange: maximum range in yards.
        - longtohit: chance to hit per gun per minute at long range.
        - longmin: minimum range in yards considered to be long range.
        - effectivetohit: chance to hit per gun per minute at effective range.
        - effectivemin: minimum range in yards considered to be effective.
        - shorttohit: chance to hit per gun per minute at short range.
    """

    def __init__(self, caliber, maxrange, longtohit, longmin, effectivetohit, effectivemin, shorttohit):
        self.caliber = caliber
        self.maxrange = maxrange
        self.longtohit = longtohit
        self.longmin = longmin
        self.effectivetohit = effectivetohit
        self.effectivemin = effectivemin
        self.shorttohit = shorttohit

    def return_to_hit(self, targetrange):
        """Return the chance to hit (per gun and minute) for a given range. If the target is out of range, return 0."""
        if targetrange > self.maxrange:
            return 0
        elif targetrange > self.longmin:
            return self.longtohit
        elif targetrange > self.effectivemin:
            return self.effectivetohit
        elif targetrange >= 0:
            return self.shorttohit
        else:
            raise ValueError("Range must be a positive integer")


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

    gundict = {}
    with open(filename) as sourcefile:
        reader = csv.reader(sourcefile, delimiter="\t")
        next(reader)
        for row in reader:
            gundata = list(row)
            gundict[gundata[0]] = list(map(float, gundata[1:]))
    return gundict

# Build the gun dictionary for capital ships
capitalguns = build_gun_dictionary("capital_weapons.csv")

# Build the gun dictionary for cruisers

# Build the gun dictionary for destroyers
