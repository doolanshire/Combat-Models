#!/usr/bin/python

import matplotlib.pyplot as plt
import random
import math

class Target:
	"""
	A circular target with a fixed radius. The target is created by defining
	its centre with cartesian coordinates (x,y) and specifying its radius.
	
	x, y (floats): target centre coordinates.
	radius (float): the radius of the target (default 1)
	--------
	angle (float): polar angle from the point (0, 0). Calculated upon init.
	distance (float): polar distance from the point (0, 0) Calculated upon init.
	hit: whether the target has been hit by a fragment. "False" upon init.
	"""
	
	def __init__(self, x, y, radius = 1):
		self.x = x
		self.y = y
		self.angle = (math.degrees(math.atan2(y,x)) + 360) % 360
		self.distance = math.sqrt(x**2 + y**2)
		self.radius = radius
		self.hit = False
		
	def get_arc(self):
		"""Return the angles (in degrees) of the two tangents to the target
		that pass through the point of origin (0, 0).
		
		RETURNS:
			- A tuple containing both angles.
		"""
		tangentDelta = math.degrees(math.asin(self.radius/self.distance))
		# Apply the theta difference both ways from the centre.
		firstTangentAngle = self.angle - tangentDelta
		secondTangentAngle = self.angle + tangentDelta
		# Return a tuple with the theta of both tangents from (0, 0).
		return (firstTangentAngle, secondTangentAngle)
		
	def polar_distance(self, other):
		"""
		Return the distance between this Target object's centre point, and
		that of another Target object.
		
		ARGUMENTS:
			- other (Target object to calculate the distance to)
		
		RETURNS:
			- The distance as a float.
		"""
		x1, x2 = self.x, other.x
		y1, y2 = self.y, other.y
		polarDistance = math.sqrt((x1-x2)**2 + (y1-y2)**2)
		return polarDistance
		
	def is_too_close(self, other, minimum):
		"""Return True if this Target is too close to another, False otherwise.
		
		
		ARGUMENTS:
			- other (Target object)
			– minimum (float): the minimum distance that can exist between two
			targets, measured from their edges. Radius is taken into account,
			to avoid overlapping).
			
		RETURNS:
			- boolean.
		"""
		if self.polar_distance(other) <= minimum + self.radius * 2:
			return True
		else:
			return False
			
	def is_hit(self):
		return self.hit
		
	def mark_as_hit(self):
		self.hit = True
			
class Area:
	"""
	An area (x * y) to be populated by Targets randomly.
	- x (int): the x dimension.
	- y (int): the y dimension.
	- targetSize (int): the radius of all Targets in the area. Defaults to 1.
	- minimumDistance (int): the minimum acceptable distance between Targets.
	--------
	- targets (list): a list of all Targets in the area.
	- overkill (int): number of fragments wasted hitting Targets that had
	already been hit. Value 0 at init.
	"""
	def __init__(self, x, y, minimumDistance, targetSize = 1):
		self.x = x
		self.y = y
		self.targetSize = targetSize
		self.minimumDistance = minimumDistance
		self.targets = []
		self.overkill = 0

	def add_random_target(self):
		"""Attempt to add one random target to the area.
		
		RETURNS:
			- True if the Target was added successfully (did not land at an
			illegal distance from another Target). False otherwise.
		"""
		# Propose a Target location at random inside the area.
		attempted_x = random.uniform(-self.x//2, self.x//2)
		attempted_y = random.uniform(-self.y//2, self.y//2)
		attempted_target = Target(attempted_x, attempted_y, self.targetSize)
		# Check distance of this proposed Target to all other Targets.
		for target in self.targets:
			# Return 'False' if the attempted Target is too close to another.
			if attempted_target.is_too_close(target, self.minimumDistance):
				return False
			# Reserve the middle spot for the origin of the blast.
			if attempted_target.is_too_close(Target(0,0,self.targetSize), self.minimumDistance):
				return False
		# Add the Target to the area if it is not too close to any other.
		self.targets.append(attempted_target)
		return True
		
	def populate(self, targets):
		"""
		Attempt to add (targets) amount of targets to the area.
		
		ARGUMENTS:
			- targets (int): the number of targets to attempt to place.
		"""
		print("Attempting to place {} targets".format(targets))
		failed = 0
		for _ in range(targets):
			# Attempt to place one target.
			attempt = self.add_random_target()
			# If the target cannot be placed, add one to the "failed" counter.
			if attempt == False:
				failed += 1
		
		# Print how many Targets failed placement.
		print("Failed to place {} targets".format(failed))
		# Calculate and print the percentage of the area covered by Targets.
		targetArea = (self.targetSize**2 * math.pi) * len(self.targets)
		percentCovered = (targetArea / (self.x * self.y)) * 100
		print("Percent covered: {}".format(percentCovered))
		# Sort all targets by proximity to the centre (0, 0).
		print("Sorting targets by proximity to the centre")
		self.targets.sort(key=lambda x: x.distance)
		print("Sorted!")
		
	def plot(self):
		"""The area goes plot itself."""
		# Find the (x, y) coordinates of all intact Targets.
		x = [target.x for target in self.targets if not target.is_hit()]
		y = [target.y for target in self.targets if not target.is_hit()]
		# Find the (x, y) coordinates of all hit targets.
		xhit = [target.x for target in self.targets if target.is_hit()]
		yhit = [target.y for target in self.targets if target.is_hit()]
		# Plot intact targets in blue, hit in red.
		plt.scatter(x, y, marker="o", s=10, facecolors="none", edgecolors="b")
		plt.scatter(xhit, yhit, marker="o", s=10, facecolors="none", edgecolors="r")
		# Mark the origin of the explosion.
		plt.scatter(0,0, marker="*", s=50, facecolors="none", edgecolors="orange")
		# Plot a line to the centre of each hit target (temporary).
		for i, j in zip(xhit, yhit):
			plt.plot((0, i), (0, j), c="orange", linestyle=":")
		plt.show()

	def check_LOS(self, angle):
		"""
		Check whether a Target would be hit by a fragment travelling down a
		specified angle. If it would, and the target had not been hit before,
		mark it as "hit". If it had already been hit, add one to the "overkill"
		counter.
		
		ARGUMENTS:
			- angle (float): the angle to check for.
			
		RETURNS:
			- True (and hence stops execution) if a Target is hit.
		"""
		
		# Iterate over all targets in increasing order of distance from (0, 0).
		for target in self.targets:
			lower, higher = target.get_arc()[0], target.get_arc()[1]
			# Check whether the fragment angle lies between the tangents.
			if lower <= angle <= higher:
				# Mark the target as hit if it had not been hit before.
				if not target.is_hit():
					target.mark_as_hit()
				# Otherwise, add 1 to the "overkill" counter.
				else:
					self.overkill += 1
				# Stop execution if a target has been hit.
				return True
				
	def explosion(self, fragments):
		"""
		Create an explosion with a given number of fragments. Makes a list of
		(fragments) floats between 0 and 360. Then checks whether there are
		any targets in a straight line in that bearing, using the check_LOS()
		function. Targets are marked as hit when applicable.
		
		ARGUMENTS
		– fragments (int): the number of fragments to generate.
		"""
		fragmentDirections = [random.uniform(0, 360) for _ in range(fragments)]
		for fragment in fragmentDirections:
			self.check_LOS(fragment)
			
	def get_kills(self):
		return sum(1 for target in self.targets if target.is_hit())



area = Area(200, 200, 1, 1)
area.populate(300)
area.explosion(200)
print(area.get_kills())

area.plot()
print(area.overkill)