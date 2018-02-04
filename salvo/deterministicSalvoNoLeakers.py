#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 2017

@author: Alvaro Radigales

A Python implementation of the Deterministic Salvo Model created by Wayne P. Hughes Jr.

The results are consistent with those found in the works of Hughes, Cares, McGunnigle,
Tiah et al. The included classes have been given default values in some attributes to
account for the different versions of the model.


"""

import matplotlib.pyplot as plt
import numpy as np

class Ship:
    ''' A ship carrying anti-ship cruise missiles.
    
    Attributes:
        * type (str): the type of ship, for labeling purposes only.
        * op (int): the number of anti-ship cruise missiles the ship can fire in one salvo.
        * dp (int): the number of SAM the ship can fire in one salvo against incoming missiles.
        * sp (float): initial staying power in missile hits.
        * hp (float): hit points remaining.
        * status (fraction): fraction of its staying power remaining. 1 is intact, 0 is OOA.
    '''
    
    def __init__(self, type, op, dp, sp):
        self.type = type
        self.op = op
        self.dp = dp
        self.sp = sp
        self.hp = sp
        self.status = 1
        
    def damage(self, damage):
        ''' Lowers the ship's 'hp' attribute by the input amount.
        
        Args:
            * damage (float): points of damage to subtract. HP cannot go below 0.
        '''
        damage = min(damage, self.hp)
        damage = max(damage, 0)
        self.hp -= damage
        self.status = self.hp / self.sp
        
    def ascm_fire(self):
        ''' Returns cruise missile salvo size based on status.'''
        return self.op * self.status
        
    def sam_fire(self):
        ''' Returns SAM salvo size based on status.'''
        return self.dp * self.status
        
    def __str__(self):
        ''' String override. Returns ship type, status as percentage, OP, and DP.'''
        shipStatus = round(self.status * 100, 2)
        shipOp = round(self.ascm_fire(), 2)
        shipDp = round(self.sam_fire(), 2)
        shipString = "{} ({}%) OP: {} DP: {}\n".format(self.type, shipStatus, shipOp, shipDp)
        return shipString
        
class Missiles:
    ''' The specification of the missile systems carried by a group of ships.
    
    Attributes:
        * launch_reliability (fraction): fraction of cruise missiles that launch successfully.
        * ascm_to_hit (fraction): fraction of cruise missiles that hit, in the absence of defences.
        * sam_to_hit (fraction): fraction of SAM that successfully intercept incoming missiles.
    '''
    def __init__(self, launch_reliability = 1, ascm_to_hit = 1, sam_to_hit = 1):
        self.launch_reliability = launch_reliability
        self.ascm_to_hit = ascm_to_hit
        self.sam_to_hit = sam_to_hit
        
    def offensive_modifier(self):
        ''' Returns the fraction of missiles that launch AND hit.'''
        return self.launch_reliability * self.ascm_to_hit

class Group:
    ''' A group of ships.
    
    Attributes:
        * side (str): the group's side identifier, for labelling purposes.
        * ship (Ship): the ship type the group is composed of.
        * units (int): the number of ships of type (ship) in the group.
            * oob (list): a list of Ship objects representing the group.
        * scouting (fraction): fraction of enemy group that can be located and targeted.
        * readiness (fraction): efficiency of the group's defences.
        * missiles (Missiles): the missile systems used by the group.
    '''
    def __init__(self, side, ship, units, scouting = 1, readiness = 1, missiles = Missiles()):
        self.side = side
        self.oob = [Ship(ship.type, ship.op, ship.dp, ship.sp) for i in range(units)]
        self.scouting = scouting
        self.readiness = readiness
        self.missiles = missiles
        
    def striking_power(self):
        ''' Returns the raw striking power of the group.'''
        salvoSize = sum(ship.ascm_fire() for ship in self.oob)
        strikingPower = salvoSize * self.scouting * self.missiles.offensive_modifier()
        return strikingPower
        
    def defensive_power(self):
        ''' Returns the raw defensive power of the group.'''
        defensiveSalvoSize = sum(ship.sam_fire() for ship in self.oob)
        defensivePower = defensiveSalvoSize * self.readiness * self.missiles.sam_to_hit
        return defensivePower
        
    def combat_power(self, enemy):
        ''' Returns the combat power in excess of the enemy's defences.
        
        Arguments:
            * enemy (Group): the target group.
        '''
        return max(0, (self.striking_power() - enemy.defensive_power()))
        
    def total_status(self):
        ''' Returns the sum of the 'status' attributes of all ships in the group.'''
        return sum(i.status for i in self.oob)
        
    def damage(self, damage):
        ''' Damages the group. Applied to all ships consecutively until damage reaches
        zero, or no more targets are available.
        
        Arguments:
            * damage (float): the total amount damage to inflict upon the group.
        ''' 
        while damage > 0 and self.total_status() > 0:
            for i in self.oob:
                if i.status > 0:
                    if damage > i.hp:
                        damage -= i.hp
                        i.damage(i.hp)
                    else:
                        i.damage(damage)
                        damage = 0
        
    def __str__(self):
        ''' String override. Returns the percentage of the original staying power remaining,
        and the (equivalent) number of active ships.
        '''
        percentage = round((self.total_status() / len(self.oob)) * 100, 2)
        activeShips = round(self.total_status(), 2)
        groupString = "{}: {}% ({} active ships)".format(self.side, percentage, activeShips)
        return groupString
        
class Battle:
    ''' A battle between two groups.
    
    Attributes:
        * blu (Group): the BLUFOR group.
        * red (Group): the REDFOR group.
        * duration (int): the duration of the battle in pulses. If zero (default) the
        battle goes on until one side is wiped out.
    '''
    def __init__(self, blu, red, duration = 0):
        self.blu = blu
        self.red = red
        self.duration = duration
        self.pulse = 0
        # Lists for plotting
        self.bluPlot = [self.blu.total_status()]
        self.redPlot = [self.red.total_status()]
        self.time = [0]
        
    def add_to_plot(self):
        self.bluPlot.append(self.blu.total_status())
        self.redPlot.append(self.red.total_status())
        self.time.append(self.pulse)
        
    def stalemate(self):
        ''' Checks whether the battle has reached a stalemate. Only possible if SAM fire
        is 100% effective for both sides (missile sam_to_hit = 1)'''
        stalemate = self.blu.combat_power(self.red) == 0 and self.red.combat_power(self.blu) == 0
        return stalemate
        
    def blu_surprise(self):
        ''' Fires one BLUFOR salvo at REDFOR, without retaliation.'''
        if self.pulse == 0:
            print("\nBattle starts between {} and {}\n".format(self.blu.side, self.red.side))
            print(self)
        self.pulse += 1
        self.red.damage(self.blu.combat_power(self.red))
        print(self)
        # Add new values to the plotting lists
        self.add_to_plot()
        
    def red_surprise(self):
        ''' Fires one REDFOR salvo at BLUFOR, without retaliation.'''
        if self.pulse == 0:
            print("\nBattle starts between {} and {}\n".format(self.blu.side, self.red.side))
            print(self)
        self.pulse += 1
        self.blu.damage(self.red.combat_power(self.blu))
        print(self)
        # Add new values to the plotting lists
        self.add_to_plot()
        
    def salvo(self):
        ''' Both sides fire at each other simultaneously.'''
        if self.pulse == 0:
            print("\nBattle starts between {} and {}\n".format(self.blu.side, self.red.side))
            print(self)
        bluDamageSustained = self.red.combat_power(self.blu)
        redDamageSustained = self.blu.combat_power(self.red)
        self.blu.damage(bluDamageSustained)
        self.red.damage(redDamageSustained)
        self.pulse += 1
        print(self)
        # Add new values to the plotting lists
        self.add_to_plot()
        
    def resolve(self):
        ''' The battle is resolved for the specified duration, or until one side is wiped out.'''
        if self.duration == 0:
            while self.blu.total_status() != 0 and self.red.total_status() != 0:
                self.salvo()
                # Add new values to the plotting lists
                self.add_to_plot()
                if self.stalemate():
                    print("\nStalemate! Neither fleet can penetrate enemy missile defence.")
                    break
        else:
            for _ in range(self.duration):
                self.salvo()
                # Add new values to the plotting lists
                self.add_to_plot()

    

    def plot(self):
        x = np.array(self.time)
        y = np.array(self.bluPlot)
        z = np.array(self.redPlot)
        
        width = 0.2
        
        fig, ax = plt.subplots()
        rects1 = ax.bar(x-0.1, y, width, color='tab:blue', zorder=3)
        rects2 = ax.bar(x+0.1, z, width, color='tab:red', zorder=3)
        
        ax.set_ylabel('Aggregated status')
        ax.set_xlabel('Pulse')
        
        ax.set_xticks(x)
        #ax.set_yticks(np.arange(0,max(max(y),max(z))+1,1))
        
        ax.legend((rects1[0],rects2[0]),(self.blu.side,self.red.side), loc=9)
        
        ax.grid(which='major', axis='y', linestyle=':', alpha=0.5, zorder=0)
        ax.grid(which='minor', axis='y', linestyle=':', alpha=0.25, zorder=0)
        
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., height,
                '{}'.format(round(height,2)),
                ha='center', va='bottom')
        
        autolabel(rects1)
        autolabel(rects2)
        plt.show()
        
        
    def __str__(self):
        ''' String override. Returns the pulse number, and the status of the opposing groups.'''
        battleString = "\nPulse {}:\n{} | {}".format(self.pulse, str(self.blu), str(self.red))
        return(battleString)
    
# Test battle. Scenario taken from Cares, page 23, Scenario VI

# Knox-Class frigate     
frigate = Ship("Frigate", 4, 4, 2)
# String override demo
print(frigate)

# Anti-Ship Cruise Missiles and SAM used by both groups
#basic = Missiles()
standard = Missiles(1,0.61,0.35)

# Group creation
blufor = Group("BLUFOR", frigate, 2, 1, 1, standard)
redfor = Group("REDFOR", frigate, 3, 1, 1, standard)

# Battle creation, no duration specified
battle = Battle(blufor, redfor)

# Battle resolves until one side is wiped out
#battle.blu_surprise()
#battle.salvo()
battle.salvo()
battle.plot()