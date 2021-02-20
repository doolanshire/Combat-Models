import seaborn as sns
import matplotlib.pyplot as plt


def strength_plot(battle):
    """A simple line plot of the fighting strength of both sides of a naval engagement.

    Attributes:
        - battle: a Battle object involving two sides.
    """
    sns.set_theme()
    blue = sns.lineplot(data=battle.side_a_staying_power, label=battle.side_a.name)
    red = sns.lineplot(data=battle.side_b_staying_power, label=battle.side_b.name)
    blue.set(xlabel="Time", ylabel="Staying power (6-inch hits)")
    plt.title(battle.name)
    plt.show()


def firepower_comparison(group_a, group_b):
    """A graph comparing the firepower of two groups at different distances."""
    max_a_range = max(ship.main_armament_type.max_range for ship in group_a.members)
    max_b_range = max(ship.main_armament_type.max_range for ship in group_b.members)
    longest = max(max_a_range, max_b_range)
    group_a_firepower = []
    for i in range(0, int(longest), 100):
        firepower = sum(ship.main_armament_type.return_equivalent_damage(i) * ship.main_armament_broadside for ship
                        in group_a.members)
        group_a_firepower.append(firepower)
    group_b_firepower = []
    for i in range(0, int(longest), 100):
        firepower = sum(ship.main_armament_type.return_equivalent_damage(i) * ship.main_armament_broadside for ship
                        in group_b.members)
        group_b_firepower.append(firepower)

    sns.set_theme()
    blue = sns.lineplot(data=group_a_firepower, label=group_a.name)
    red = sns.lineplot(data=group_b_firepower, label=group_b.name)
    blue.set(xlabel="Range in thousands of yards", ylabel="Equivalent 6-inch hits")
    ticks = blue.get_xticks().tolist()
    ticks = [i // 10 for i in ticks]
    blue.set_xticklabels(ticks)
    plt.title("Firepower comparison")
    plt.show()
