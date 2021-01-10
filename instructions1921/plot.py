import seaborn as sns
import matplotlib.pyplot as plt


def strength_plot(battle):
    """A simple line plot of the fighting strength of both sides of a naval engagement.

    Attributes:
        - battle: a Battle object involving two sides.
    """
    sns.set_theme()
    blue = sns.lineplot(data=battle.a_plot, label=battle.side_a.name)
    red = sns.lineplot(data=battle.b_plot, label=battle.side_b.name)
    blue.set(xlabel="Time", ylabel="Staying power (6-inch hits)")
    plt.show()
