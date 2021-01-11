#!/usr/bin/python

import numpy as np
import pandas as pd

def gun_regression(gun):
	"""Takes a row from a pandas dataframe containing gun data and returns a NumPy array containing
	the terms of a logarithmic regression function fitting the gun data."""
	long_range = (gun["max_range"] + gun["long_min"]) / 2
	effective_range = (gun["long_min"] + gun["effective_min"]) / 2
	short_range = (gun["effective_min"] / 2)
	x = [long_range, effective_range, short_range]
	y = [gun["long_to_hit"], gun["effective_to_hit"], gun["short_to_hit"]]
	return(np.polyfit(np.log(x), y, 1))


def update_gun_csv(file_name):
	input_file = pd.read_csv(file_name)
	print("File loaded...")
	input_file["first_regression_term"] = input_file.apply(lambda row: gun_regression(row)[0], axis=1)
	print("First regression term added...")
	input_file["second_regression_term"] = input_file.apply(lambda row: gun_regression(row)[1], axis=1)
	print("Second regression term added...")
	return input_file

old_file = "gun_data/secondary_guns.csv"
new_file = update_gun_csv(old_file)
new_file_name = old_file[:-3] + "_interpolated.csv" 
new_file.to_csv(new_file_name, index=False)
print("New file written successfully!")
