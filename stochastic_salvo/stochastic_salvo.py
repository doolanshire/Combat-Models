#!/usr/bin/env python3

"""
Created on Thu May 21 2026

@author: Alvaro Radigales

A Python implementation of the stochastic version of Hughes' Salvo Model created by Michael
J. Armstrong and Michael B. Powell in 2005 to analyse the Battle of the Coral Sea.

"""

import copy
import logging
import matplotlib.pyplot as plt
import random

debug_log = logging.getLogger("Debug")
logging.basicConfig(level=logging.WARNING)

class Fleet:
	def __init__(self, name, ships):
		self.name = name
		self.ships = ships
		
	def damage_fleet(self, damage):
		for ship in self.ships:
			if damage > 0:
				damage_caused = min(ship.staying_power, damage)
				ship.staying_power -= damage_caused
				damage -= min(damage_caused, damage)
				
	def intercept(self):
		intercept_damage = 0
		for ship in self.ships:
			for squadron in ship.fighter_squadrons:
				intercept_roll = random.random()
				if intercept_roll < squadron.intercept_probability:
					intercept_damage += squadron.interception_damage()
					debug_log.debug(f"Squadron from {self.name} intercepts ({intercept_roll}) causing {intercept_damage} damage.")
				else:
					debug_log.debug(f"Squadron from {self.name} fails to intercept!")
				
		return intercept_damage
				
	def attack(self, target_fleet):
		damage_scored = 0
		interceptor_damage = target_fleet.intercept()
		for ship in self.ships:
			for squadron in ship.attack_squadrons:
				attack_roll = random.random()
				if attack_roll < squadron.attack_probability:
					damage_sustained = min(squadron.staying_power, interceptor_damage)
					squadron.staying_power -= damage_sustained
					interceptor_damage -= damage_sustained
					damage_scored += squadron.attack()
					debug_log.debug(f"Attack squadron suffers {damage_sustained} damage and attacks for {squadron.staying_power} damage.")
				else:
					debug_log.debug(f"Attack squadron fails to attack!")
		
		debug_log.debug(f"Total strike damage is {damage_scored}")
					
		target_fleet.damage_fleet(damage_scored)
		

class Carrier:
	def __init__(self, attack_squadrons, fighter_squadrons):
		self.attack_squadrons = attack_squadrons
		self.fighter_squadrons = fighter_squadrons
		self.staying_power = 1
		
class AttackSquadron:
	def __init__(self, attack_probability):
		self.attack_probability = attack_probability
		self.staying_power = 1
		
	def damage(self, damage_received):
		self.staying_power -= min(damage_received, self.staying_power)
		
	def attack(self):
		if self.staying_power > 0:
			return 1
		else:
			return 0

class FighterSquadron:
	def __init__(self, intercept_probability, mean_damage, damage_deviation):
		self.intercept_probability = intercept_probability
		self.mean_damage = mean_damage
		self.damage_deviation = damage_deviation
		
	def interception_damage(self):
		return (self.mean_damage + self.damage_deviation * (2 * random.random() - 1))
	
def run_experiment(us_fleet, jp_fleet, iterations):
	us_staying_power = sum(ship.staying_power for ship in us_fleet.ships)
	jp_staying_power = sum(ship.staying_power for ship in jp_fleet.ships)
	us_losses = []
	jp_losses = []
	for i in range(iterations):
		us_fleet_instance = copy.deepcopy(us_fleet)
		jp_fleet_instance = copy.deepcopy(jp_fleet)
		
		us_fleet_instance.attack(jp_fleet_instance)
		jp_fleet_instance.attack(us_fleet_instance)
		
		us_new_staying_power = sum(ship.staying_power for ship in us_fleet_instance.ships)
		jp_new_staying_power = sum(ship.staying_power for ship in jp_fleet_instance.ships)
		
		us_losses.append(us_staying_power - us_new_staying_power)
		jp_losses.append(jp_staying_power - jp_new_staying_power)
		
	average_us_losses = sum(us_losses) / len(us_losses)
	average_jp_losses = sum(jp_losses) / len(jp_losses)
	
	return average_us_losses, average_jp_losses

us_f_squadron = [FighterSquadron(0.2857, 1, 0.3333)]
us_attack_squadrons = [AttackSquadron(0.4762)] * 3

jp_f_squadron = [FighterSquadron(0.4286, 1, 0.3333)]
jp_attack_squadrons = [AttackSquadron(0.6429)] * 2

us_carrier = Carrier(us_attack_squadrons, us_f_squadron)

jp_carrier = Carrier(jp_attack_squadrons, jp_f_squadron)

us_fleet = Fleet("US Fleet", [us_carrier] * 2)

jp_fleet = Fleet("JP Fleet", [jp_carrier] * 2)

experiment_results = run_experiment(us_fleet, jp_fleet, 1000)

print(experiment_results)
