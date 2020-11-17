import seaborn as sns
import matplotlib.pyplot as plt


def strength_plot(side_a, side_b):
    """A simple line plot of the fighting strength of both sides of a naval engagement.

    Attributes:
        - sidedA / sideB: lists detailing the hit points of each side at every consecutive time pulse."""
    sns.set_theme()
    sns.lineplot(data=side_a)
    sns.lineplot(data=side_b)
    plt.show()
