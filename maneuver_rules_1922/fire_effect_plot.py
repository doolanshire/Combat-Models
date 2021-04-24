"""This short script makes a plot of all columns of a fire effect table (with range as the indes) to visually
check for bad input values.
"""

import matplotlib.pyplot as plt
import pandas as pd

file_name = '6-in-53_percent_plane.csv'
file_directory = 'fire_effect_tables/1922/6-in-53/'
file_path = file_directory + file_name

gun_data = pd.read_csv(file_path, index_col='range', na_values="--", dtype=float)

print(gun_data)
gun_data.plot(title=file_name, marker='o', ms=3)
plt.show()
