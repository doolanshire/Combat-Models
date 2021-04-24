"""This short script makes a plot of all columns of a fire effect table (with range as the indes) to visually
check for bad input values.
"""

import matplotlib.pyplot as plt
import pandas as pd

fire_effect_tables_edition = "1922"
gun_designation = '6-in-50'
spot_type = 'top'

file_path = "fire_effect_tables/{}/{}/{}_percent_{}.csv".format(fire_effect_tables_edition, gun_designation,
                                                                gun_designation, spot_type)

gun_data = pd.read_csv(file_path, index_col='range', na_values="--", dtype=float)

print(gun_data)
gun_data.plot(title="{} {}".format(gun_designation, spot_type), marker='o', ms=3)
plt.show()
