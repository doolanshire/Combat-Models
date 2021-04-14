#!/usr/bin/python

import configparser
import csv

# String ID of the battle
battle = "cocos"


def parse_battle_cfg(battle_ID_string):
	"""Parse the config file for a battle from that battle's ID string."""
	# Initialise the parser
	battle_config = configparser.ConfigParser()
	# Build the battle data path string
	battle_data_path = "battle_data/{}/{}.cfg".format(battle_ID_string, battle_ID_string)
	# Load the cfg file into a dictionary
	battle_config.read(battle_data_path)
	#battle_data = dict(parser.items("General"))
	return battle_config

def parse_group_data(battle_ID_string):
	"""Parse the group data for a battle from that battle's ID string."""
	# Build the group data paths
	group_data_path = "battle_data/{}/".format(battle_ID_string)
	side_a_path = group_data_path + "side_a_groups.csv"
	side_b_path = group_data_path + "side_b_groups.csv"
	# Make the group dictionary for side A
	side_a_group_dictionary = {}
	with open(side_a_path) as input_file:
		side_a_groups = csv.reader(input_file, delimiter=',')
		next(side_a_groups, None)
		for row in side_a_groups:
			name = row[0]
			ships = row[1].split(",")
			type = row[2]
			side_a_group_dictionary[name] = (ships, type)
	# Make the group dictionary for side B
	side_b_group_dictionary = {}
	with open(side_b_path) as input_file:
		side_b_groups = csv.reader(input_file, delimiter=',')
		next(side_b_groups, None)
		for row in side_b_groups:
			name = row[0]
			ships = row[1].split(",")
			type = row[2]
			side_b_group_dictionary[name] = (ships, type)
			
	return (side_a_group_dictionary, side_b_group_dictionary)

# Print the name of the battle from the CFG file
print(parse_battle_cfg("cocos")["General"]["name"])
# Print the group data dictionaries
for group in parse_group_data(battle):
	print(group)
