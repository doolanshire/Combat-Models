import seaborn as sns
import matplotlib.pyplot as plt


def strength_plot(side_a, label_a, side_b, label_b):
    """A simple line plot of the fighting strength of both sides of a naval engagement.

    Attributes:
        - sidedA / sideB: lists detailing the hit points of each side at every consecutive time pulse."""
    sns.set_theme()
    blue = sns.lineplot(data=side_a, label=label_a)
    red = sns.lineplot(data=side_b, label=label_b)
    blue.set(xlabel="Time", ylabel="Staying power (6-inch hits)")
    plt.show()
