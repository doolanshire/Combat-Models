# Fulkerson's Air Game

A quick simulation of Fulkerson's 1957 Tactical Air Game, as described here:

https://www.rand.org/content/dam/rand/pubs/papers/2007/P1063.pdf


## Description

Two air forces face each other over a series of discrete combat phases.

Aircraft are assigned one of two roles:
* **Airfield attack**: destroying the enemy air assets on the ground.
* **Close Air Support (CAS)**: attacking enemy ground units.

Each force scores points by flying CAS missions. The number of points is the number of
aircraft assigned to CAS duty, multiplied by an arbitrary payoff factor.

Airfield attack missions score no points, but deplete the enemy air pool, and hence
impair the enemy's ability to earn points.

This is a zero-sum game: what blue wins, red loses. Hence, the final score is a single
number, which is positive if it favours blue, and negative if it favours red.