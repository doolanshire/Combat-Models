#!/usr/bin/python

import math

def oblicalc(target_angle, angle_of_fall, inclination, rotation=90):
	"""Return the oblicuity angle of a shell hitting a ship's armour plate.

	All measurement conventions have been kept from Nathan Okun's OBLICALC.EXE program. Pitch and roll
	are not considered, as they don't apply in the Naval War College's wargame.
	
	Arguments:
		- target_angle (float): the angle in degrees between the line of fire and the target's keel,
		  measured clockwise from the target's bow.
		- angle_of_fall (float): the angle in degrees between the shell's trajectory and the horizontal plane,
		  measured up from the sea surface.
		- inclination (float): the inclination in degrees of the ship's armour plate, with an input of 0
		  meaning the armour plate is vertical. A negative input means the plate slopes away from the firer,
		  and faces up. A positive input means the top overhangs the bottom and the plate faces down.
		- rotation (float): the rotation of the plate on the deck plane, measured clockwise from the target's
		  bow. The default input of 90 degrees means the plate is parallel to the keel.
	"""

	# Convert inputs to radians.
	target_angle = math.radians(target_angle)
	angle_of_fall = math.radians(angle_of_fall)
	inclination = math.radians(inclination)
	rotation = math.radians(rotation)
	
	# Aggregate target angle and plate rotation.
	target_angle = target_angle + rotation - math.radians(90)
	
	# Calculate the obliquity from the plate's normal.
	obliquity = math.acos(math.cos(inclination) * math.sin(target_angle) * math.cos(angle_of_fall)
						  - math.sin(inclination) * math.sin(angle_of_fall))
						
	# Convert back to degrees
	obliquity = math.degrees(obliquity)
	
	return obliquity

print(oblicalc(83, 12, -60))
