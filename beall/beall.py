# Thomas Reagan Beall's Naval Combat Model (1990)
# ===============================================
# NOTE: all firepower values are defined in TPBE
# (Thousand-Pound Bomb Equivalent) by the weight
# of explosive ordnance fired. See:
# BEALL, Thomas R – The Development of a Naval
# Battle Model and its Validation Using Historical
# Data – Naval Postgraduate School (1990).
# ===============================================

class Group:
    """ A group of ships.
    Parameters:
    - name (string) - the name of the group, for output labelling purposes.
    - continuousFire (float) - the continuous fire value of the group, in TPBE
    - staying (float) – the staying power of the group.
    Additional attribute:
    - pulse (list) - a list of pulse weapons (torpedoes, bombs) added by the
    "add_pulse_weapon()" method.
    """
    
    def __init__(self, name, continuousFire, staying):
        self.name = name
        self.continuousFire = continuousFire
        self.originalStaying = self.previousStaying = self.staying = staying
        self.pulse = [] # An empty list, to store pulse weapons later.
        
    def add_pulse_weapon(self, power, number):
        """ Adds a pulse weapon platform to the group.
        
        power (float) = the theoretical destructive power (TPBE) of a SINGLE weapon (torpedo,
        bomb, etc) in the platform.
        number (int) = the number of weapons the group can fire in a single salvo.
        """
        
        pp = (power, number)
        self.pulse.append(pp)
        
    def get_status(self):
        """ Returns the status of the group in the current minute."""
        return self.staying / self.originalStaying
        
    def previous_status(self):
        """ Returns the status of the group in the previous minute."""
        return self.previousStaying / self.originalStaying
        
    def continuous_fire(self):
        return self.continuousFire * self.previous_status()
        
    def pulse_fire(self, type = 'all', salvoSize = 'all'):
        """ Returns the pulse fire value of the group.
        
        If nothing is specified, it returns the total theoretical pulse fire of the group
        (full salvos from all platforms)
        
        type = the index of the type of weapon fired (starts at 0)
        salvoSize = the number of weapons from the platform fired in one salvo.
        
        Before being returned, the value is modified by the group's status.
        
        The function cannot return a value higher than the theoretical maximum (a group
        with 24 torpedo tubes cannot fire 25 torpedoes)
        """
        
        if type == 'all':
            # Return the total theoretical pulse power of the group
            salvo = sum(weapon[0] * weapon[1] for weapon in self.pulse)
            return salvo * self.previous_status()
        else:
            # Return the total theoretical pulse power for a specific type of weapon
            if salvoSize == 'all':
                # If the group is assumed to fire a full salvo
                salvo = self.pulse[type][0] * self.pulse[type][1]
                return salvo * self.previous_status()
            else:
                # If the number of weapons in the salvo is specified
                salvo = self.pulse[type][0] * min(salvoSize, self.pulse[type][1])
                return salvo * self.previous_status()
                
    def damage(self, ratio):
        """ Damages the group by a given fractional ratio (damage by 0.5 would damage
        the group by 50%)
        
        ratio (fraction) = the damage applied to the group from 0 to 1. All values equal
        to 1 or higher, which would result in no damage or negative damage, are ignored.
        """
        
        if ratio < 0:
            self.staying *= 0
        if ratio <= 1:
            self.staying *= ratio
            
    def refresh(self):
        """ Refreshes the group by advancing time one minute. The current staying power
        becomes the previous one.
        """ 
        
        self.previousStaying = self.staying
        
    def __str__(self):
        """ String override"""
        sp = round(self.staying, 3)
        cf = round(self.continuous_fire(), 3)
        pf = round(self.pulse_fire(), 3)
        groupString = "{:<24} SP: {:<5} | CF: {:<5} | PF: {:<5}".format(self.name, sp, cf, pf)
        return groupString
        
class Side:
    """ One of two opposing sides, formed by one or more groups.
    Parameters:
    - name (string): the name of the side, for output labelling purposes.
    - groups (list): a list of the Group objects included in the side.
    """
    
    def __init__(self, name, groups):
        self.name = name
        self.groups = groups
        self.originalStaying = sum(_.staying for _ in self.groups)
        self.originalContinuous = sum(group.continuousFire for group in self.groups)
        self.originalPulse = sum(group.pulse_fire() for group in self.groups)
        self.continuousEvents = []
        self.pulseEvents = []
        self.latestEvent = 0
        
    def staying_power(self, groupSelection = 'all'):
        """ Returns the staying power of the side, in the current minute.
        
        If nothing is specified, the aggregated staying power of all groups is returned.
        
        If groupSelection is an int, return staying power for the group at index [groupSelection]
        
        If groupSelection is a tuple, return aggregated staying power for the selected groups.
        """
        
        if groupSelection == 'all':
        # Return the total staying power of all groups in the side
            return sum(group.staying for group in self.groups)
            
        elif isinstance(groupSelection, int):
        # Return the staying power for the specified group
            return self.groups[groupSelection].staying
            
        elif isinstance(groupSelection, tuple):
        # Return the aggregated staying power of the selected groups only
            return sum(self.groups[group].staying for group in groupSelection)
            
    def get_status(self):
        """ Returns the status (fraction) of the side."""
        return self.staying_power() / self.originalStaying 
        
    def continuous_fire_loss(self):
        """ Returns the percentage of continuous firepower lost by the group."""
        if self.originalContinuous == 0:
            return 0
        else:
            ratio = self.originalContinuous * self.get_status() / self.originalContinuous
            loss = (1 - ratio) * 100
            return loss
        
    def pulse_fire_loss(self):
        """ Returns the percentage of pulse firepower lost by the group."""
        if self.originalPulse == 0:
            return 0
        else:
            ratio = self.originalPulse * self.get_status() / self.originalPulse
            loss = (1 - ratio) * 100
            return loss
            
    def continuous_fire(self, groupSelection = 'all'):
        """ Returns the continuous fire value of the side.
        
        If nothing is specified, the aggregated continuous fire of all groups is returned.
        
        If groupSelection is an int, return continuous fire for the group at index [groupSelection]
        
        If groupSelection is a tuple, return the sum of continuous fire for the selected groups.
        """
        
        if groupSelection == 'all':
        # Return the total continuous fire value of all groups in the side
            return sum(group.continuous_fire() for group in self.groups)
            
        elif isinstance(groupSelection, int):
        # Return the aggregated continuous fire value for the selected group only
            return self.groups[groupSelection].continuous_fire()
            
        elif isinstance(groupSelection, tuple):
        # Return the aggregated continuous fire value of the selected groups only
            return sum(self.groups[group].continuous_fire() for group in groupSelection)
            
    def pulse_fire(self, groupSelection = 'all', type = 'all', size = 'all'):
        """ Returns the pulse fire value of the side.
        
        If nothing is specified, all groups and platforms are aggregated.
        
        If the three parameters (groupSelection, type, size) are integers, return
        the corresponding value for the specified group, weapon type, and salvo size.
        
        If groupSelection and size are tuples of the same length, return the aggregated
        value for the specified groups and their corresponding salvo sizes, matched by
        index.
        """
        
        if groupSelection == type == size == 'all':
            # Return the total maximum pulse fire of all groups and weapon types
            return sum(group.pulse_fire() for group in self.groups)
            
        elif all(isinstance(arg, int) for arg in (groupSelection, type, size)):
            # Return the pulse fire value of the specified group, weapon type, and salvo size
            return self.groups[groupSelection].pulse_fire(type, size)
            
        elif all(isinstance(arg, tuple) for arg in (groupSelection, size)) and isinstance(type, int):
            # Return the total pulse fire of weapon type [type] for selected groups and salvo sizes
            pf = sum(self.groups[group].pulse_fire(type, size[index])for index, group in enumerate(groupSelection))
            return pf
              
        else:
            raise ValueError('Invalid input for pulse fire')
            
    def damage(self, ratio, groupSelection = 'all'):
        """ Damages the groups in the side.
        
        If nothing is specified, all groups are damaged by the same ratio.
        
        If groupSelection is an int, the selected group is damaged by the given ratio.
        
        If groupSelection is a tuple, the selected groups are damaged by the given ratio.
        """
        
        if groupSelection == 'all':
            for group in self.groups:
                group.damage(ratio)
                
        elif isinstance(groupSelection, int):
            self.groups[groupSelection].damage(ratio)
            
        elif isinstance(groupSelection, tuple):
            for target in groupSelection:
                self.groups[target].damage(ratio)
        
    def continuous_fire_event(self, firer, target, efficiency, start, duration):
        """ Add a continuous fire event to the side's event list."""
        
        if start + duration > self.latestEvent:
            self.latestEvent = start + duration + 1
         
        event = (firer, target, efficiency, start, start+duration)   
        self.continuousEvents.append(event)
        
    def pulse_fire_event(self, firer, target, type, size, efficiency, start, tui):
        """ Add a pulse fire event to the side's event list."""
        
        if start + tui > self.latestEvent:
            self.latestEvent = start + tui + 1
            
        event = (firer, target, type, size, efficiency, start, start + tui)
        self.pulseEvents.append(event)
        
    def __str__(self):
        """ String override."""
        sp = round(self.staying_power(), 3)
        cf = round(self.continuous_fire(), 3)
        pf = round(self.pulse_fire(), 3)
        sideString = "{:<10s} – SP: {:<6} | CF: {:<6} | PF: {:<6}".format(self.name, sp, cf, pf)
        return sideString
        
class Battle:
    """ A battle between two opposing sides.
    Parameters:
    - name (string): name of the battle, for output labelling purposes.
    - sideA (Side object): the first of the opposing sides.
    - sideB (Side object): the second opposing side.
    Other attributes:
    - Timelines for both sides continuous and pulse fire events (lists of tuples
    specifying firer, target, time of fire, etc).
    - Lists to hold the status of each side every minute, for plotting purposes.
    - timePulse (int): the current minute of the battle. Starts at 0.
    """
    def __init__(self, name, sideA, sideB):
        self.name = name
        self.sideA = sideA
        self.sideB = sideB
        # Timelines of A and B's continuous fire events
        self.sideAtimeline = [[] for _ in range(max(self.sideA.latestEvent, self.sideB.latestEvent))]
        self.sideBtimeline = [[] for _ in range(max(self.sideA.latestEvent, self.sideB.latestEvent))]
        # Timelines of A and B's pulse fire events
        self.sideApulseEvents = [[] for _ in range(max(self.sideA.latestEvent, self.sideB.latestEvent))]
        self.sideBpulseEvents = [[] for _ in range(max(self.sideA.latestEvent, self.sideB.latestEvent))]
        # Minutes in which A and B will receive pulsed fire damage
        self.sideApulseDamage = [[] for _ in range(max(self.sideA.latestEvent, self.sideB.latestEvent))]
        self.sideBpulseDamage = [[] for _ in range(max(self.sideA.latestEvent, self.sideB.latestEvent))]
        # Status record for every minute of the battle
        self.aPlot = [(sideA.staying_power(), sideA.continuous_fire(), sideA.pulse_fire())]
        self.bPlot = [(sideB.staying_power(), sideB.continuous_fire(), sideB.pulse_fire())]
        # Time pulse of the battle, starting at 0
        self.timePulse = 0
        
        # Build the timelines for the battle from the event lists of both sides 
        
        # Side A continuous fire events
        if len(self.sideA.continuousEvents) > 0:
            for event in self.sideA.continuousEvents:
                for minute in range(event[3], event[4]):
                    self.sideAtimeline[minute].append((event[0], event[1], event[2]))
                    
        # Side B continuous fire events
        if len(self.sideB.continuousEvents) > 0:
            for event in self.sideB.continuousEvents:
                for i in range(event[3], event[4]):
                    self.sideBtimeline[i].append((event[0], event[1], event[2]))
                    
        # Side A pulse fire events
        if len(self.sideA.pulseEvents) > 0:
            for event in self.sideA.pulseEvents:
            # Append the event to the corresponding minute
                pf = (event[0], event[1], event[2], event[3], event[4], event[6])
                self.sideApulseEvents[event[5]].append(pf)
                
        # Side B pulse fire events
        if len(self.sideB.pulseEvents) > 0:
            for event in self.sideB.pulseEvents:
            # Append the event to the corresponding minute
                pf = (event[0], event[1], event[2], event[3], event[4], event[6])
                self.sideBpulseEvents[event[5]].append(pf)
                
    def advance_pulse(self):
        """ Advance the battle by one time pulse (one minute)"""
        # Check whether any A continuous fire events are taking place this minute
        if len(self.sideAtimeline[self.timePulse]) > 0:
        # Apply damage to B accordingly for each event
            for event in self.sideAtimeline[self.timePulse]:
                continuousDamage = self.sideA.continuous_fire(event[0]) * event[2]
                targetStaying = self.sideB.staying_power(event[1])
                if targetStaying == 0:
                    ratio = 0
                else:
                    ratio = max((max((targetStaying - continuousDamage), 0)/ targetStaying), 0)
                    
                self.sideB.damage(ratio, event[1])
                
        # Check whether any B continuous fire events are taking place this minute
        if len(self.sideBtimeline[self.timePulse]) > 0:
        # Apply damage to A accordingly for each event
            for event in self.sideBtimeline[self.timePulse]:
                continuousDamage = self.sideB.continuous_fire(event[0]) * event[2]
                targetStaying = self.sideA.staying_power(event[1])
                if targetStaying == 0:
                    ratio = 0
                else:
                    ratio = max((max((targetStaying - continuousDamage), 0)/ targetStaying), 0)
                    
                self.sideA.damage(ratio, event[1])
                
        # Check whether any A pulse fire events are taking place this minute
        
        # (firer, target, type, size, efficiency, start, start + tui)
        
        if len(self.sideApulseEvents[self.timePulse]) > 0:
        # Append the damage and target group to B's pulse damage timeline
            for event in self.sideApulseEvents[self.timePulse]:
                pulseDamage = self.sideA.pulse_fire(event[0], event[2], event[3]) * event[4]
                self.sideBpulseDamage[event[5]].append((event[1], pulseDamage))
                
        # Check whether any B pulse fire events are taking place this minute
        if len(self.sideBpulseEvents[self.timePulse]) > 0:
        # Append the damage and target group to B's pulse damage timeline
            for event in self.sideBpulseEvents[self.timePulse]:
                pulseDamage = self.sideB.pulse_fire(event[0], event[2], event[3]) * event[4]
                self.sideApulseDamage[event[5]].append((event[1], pulseDamage))

                
        # Check whether A is receiving any pulse damage this minute
        if len(self.sideApulseDamage[self.timePulse]) > 0:
        # Apply damage to the corresponding groups of A
            for damage in self.sideApulseDamage[self.timePulse]:
                targetStaying = self.sideA.staying_power(damage[0])
                pulseDamage = damage[1]
                if targetStaying == 0:
                    ratio = 0
                else:
                    ratio = max((max((targetStaying - pulseDamage), 0)/ targetStaying), 0)
                    
                self.sideA.damage(ratio, damage[0])
                
        # Check wheter B is receiving any pulse damage this minute
        if len(self.sideBpulseDamage[self.timePulse]) > 0:
        # Apply damage to the corresponding groups of B
            for damage in self.sideBpulseDamage[self.timePulse]:
                targetStaying = self.sideB.staying_power(damage[0])
                pulseDamage = damage[1]
                if targetStaying == 0:
                    ratio = 0
                else:
                    ratio = max((max((targetStaying - pulseDamage), 0)/ targetStaying), 0)
                    
                self.sideB.damage(ratio, damage[0])
                
        # Refresh all groups on both sides
        for group in self.sideA.groups:
            group.refresh()
        for group in self.sideB.groups:
            group.refresh()
        # Print both sides
        print(self)
        # Advance the time pulse by one unit
        self.timePulse += 1
        
    def resolve(self):
        """ Resolve the battle until its conclusion."""
        print("{:^55}".format(self.name.upper()))
        print("\n{}".format(self.sideA.name.upper()))
        for group in self.sideA.groups:
            print(group)
        
        print("\n{}".format(self.sideB.name.upper()))
        for group in self.sideB.groups:
            print(group)
        print("\n")
        battleInit = "{:<3} - {:<6} | {:<6} | {:<6} | {:<6} | {:<6} | {:<6}".format(
        "TP","SPA","CFA","PFA","SPB","CFB","PFB")
        print(battleInit)
        while self.timePulse < (len(self.sideAtimeline)) and self.sideA.staying_power() > 0 and self.sideB.staying_power() > 0:
            self.advance_pulse()
            
        print("\nSUMMARY OF LOSSES (% LOST)")
        header = "{:<5} | {:<5} | {:<5} | {:<5} | {:<5} | {:<5}".format(
        "SA", "FCA", "FPA", "SB", "FCB", "FPB")
        sa = round((1- self.sideA.get_status())*100, 2)
        sb = round((1- self.sideB.get_status())*100, 2)
        fca = self.sideA.continuous_fire_loss()
        fcb = self.sideB.continuous_fire_loss()
        fpa = self.sideA.pulse_fire_loss()
        fpb = self.sideB.pulse_fire_loss()
        lossesString = "{:<5.2f} | {:<5.2f} | {:<5.2f} | {:<5.2f} | {:<5.2f} | {:<5.2f}".format(
        sa, fca, fpa, sb, fcb, fpb)
        print(header)
        print(lossesString)
        
    def __str__(self):
        """String override."""
        sideAsp = round(self.sideA.staying_power(), 3)
        sideBsp = round(self.sideB.staying_power(), 3)
        sideAcf = round(self.sideA.continuous_fire(), 3)
        sideBcf = round(self.sideB.continuous_fire(), 3)
        sideApf = round(self.sideA.pulse_fire(), 3)
        sideBpf = round(self.sideB.pulse_fire(), 3)
        battleString = "{:<3} - {:<6.3f} | {:<6.3f} | {:<6.3f} | {:<6.3f} | {:<6.3f} | {:<6.3f}".format(
        self.timePulse,sideAsp,sideAcf,sideApf,sideBsp,sideBcf,sideBpf)
        return battleString

# CORONEL 1914 (comment out the block below if you wish to play a different battle)
britishOne = Group("Good Hope, Monmouth", 7.27, 3.21)
britishTwo = Group("Glasgow", 0.42, 1.23)

germanOne = Group("Scharnhorst, Gneisenau", 4.32, 3.30)
germanTwo = Group("Leipzig, Dresden", 4.33, 2.23)

british = Side("British", [britishOne, britishTwo])
german = Side("German", [germanOne, germanTwo])

german.continuous_fire_event(0,0,0.028,1,28)
british.continuous_fire_event(1,0,0.028,6,15)
german.continuous_fire_event(1,1,0.012, 19, 2)

battle = Battle("Coronel 1914", british, german)

battle.resolve()


# MIDWAY 1942 (uncomment the commented block below and run the file to play the battle)

# usOne = Group("Yorktown", 0, 2.07)
# usTwo = Group("Enterprise, Hornet", 0, 4.14)
# 
# usOne.add_pulse_weapon(0.4657, 19)
# usTwo.add_pulse_weapon(0.4657, 37)
# 
# usOne.add_pulse_weapon(1, 18)
# usTwo.add_pulse_weapon(1, 38)
# 
# usOne.add_pulse_weapon(0.758333333333333, 13)
# usTwo.add_pulse_weapon(0.758333333333333, 29)
# 
# japanOne = Group("Haga, Akagi, Soryu", 0, 6.33)
# japanTwo = Group("Hiryu", 0, 1.52)
# 
# japanOne.add_pulse_weapon(0.216212121212121, 54)
# japanTwo.add_pulse_weapon(0.216212121212121, 18)
# 
# japanOne.add_pulse_weapon(0.931041666666667, 68)
# japanTwo.add_pulse_weapon(0.931041666666667, 18)
# 
# us = Side("US Carrier Group", [usOne, usTwo])
# japan = Side("Japanese Carrier Group", [japanOne, japanTwo])
# 
# us.pulse_fire_event(1, 0, 1, 17, 0.162, 1, 145)
# us.pulse_fire_event(0, 1, 1, 16, 0.162, 1, 145)
# us.pulse_fire_event(0, 0, 1, 17, 0.162, 65, 81)
# us.pulse_fire_event(1, 1, 1, 24, 0.162, 470, 91)
# 
# japan.pulse_fire_event(1, 0, 0, 18, 0, 179, 61)
# japan.pulse_fire_event(1, 0, 1, 10, 0.2, 259, 91)
# 
# battle = Battle("Midway", us, japan)
# battle.resolve()


# CORAL SEA REVISED (uncomment the commented block below and run the file to play the battle)

# usOne = Group("Lexington", 0, 2.42)
# usTwo = Group("Yorktown", 0, 2.07)
# 
# usOne.add_pulse_weapon(1, 17)
# usTwo.add_pulse_weapon(1, 17)
# usOne.add_pulse_weapon(0.58, 15)
# usTwo.add_pulse_weapon(0.58, 15)
# usOne.add_pulse_weapon(0.758, 10)
# usTwo.add_pulse_weapon(0.758, 9)
# 
# japanOne = Group("Shokaku", 0, 2.42)
# japanTwo = Group("Zuikaku", 0, 2.24)
# 
# japanOne.add_pulse_weapon(0.2162, 17)
# japanTwo.add_pulse_weapon(0.2162, 16)
# japanOne.add_pulse_weapon(0.931, 13)
# japanTwo.add_pulse_weapon(0.931, 12)
# 
# us = Side("US", [usOne, usTwo])
# japan = Side("Japan", [japanOne, japanTwo])
# 
# # firer, target, type, size, efficiency, start, tui
# us.pulse_fire_event((0,1), 0, 0, (17, 17), 0.065, 47, 111)
# us.pulse_fire_event((0,1), 0, 0, (6, 6), 0.065, 47, 154)
# 
# japan.pulse_fire_event((0,1), (0,1), 0, (17, 16), 0.091, 55, 125)
# japan.pulse_fire_event((0,1), 0, 1, (9, 9), 0.111, 55, 125)
# 
# battle = Battle("Coral Sea", us, japan)
# 
# battle.resolve()

