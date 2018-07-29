''' This is a quick simulation based on Fulkerson's 1957 Tactical Air Game.

    Two air forces compete in a zero-sum game in which points are scored by
    flying CAS (Close Air Support) missions. Planes not allocated to CAS are
    automatically assumed to be flying airfield strike missions to destroy the
    enemy air force on the ground.
'''

class AirForce:
    """One of two competing air forces in a campaign.
    
    Arguments:
    name -- the name of the air force purely for labelling purposes only.
    planes -- the number of aircraft in the force.
    killRate -- the number of enemy aircraft eliminated per friendly per phase.
    CASratio -- ratio of planes dedicated to CAS duty.
    reinforcements -- number of replacement aircraft received each phase.
    """
    
    def __init__(self, name, planes, killRate, CASratio = 0, reinforcements = 0):
        self.name = name
        self.planes = planes
        self.killRate = killRate
        self.CASratio = CASratio
        self.reinforcements = reinforcements
        
    def airfield_attack(self):
        """ Returns the number of enemy aircraft kills the air force will achieve."""
        return round(int(self.planes * (1 - self.CASratio)) * self.killRate)
        
    def close_air_support(self):
        """ Returns the number of aircraft flying CAS sorties."""
        return int(self.planes * self.CASratio)
        
    def damage(self, amount):
        """ Removes the specified number of aircraft from the air force."""
        self.planes -= amount
        if self.planes < 0:
            self.planes = 0
            
    def reinforce(self):
        """ Adds the specified number of aircraft to the air force."""
        self.planes += self.reinforcements
        
class AirCampaign:
    """ A campaign between two air forces, with a set duration.
    
    Arguments:
    blue -- the blue side (an object of class AirForce)
    red -- the red side (an object of class AirForce)
    duration -- the number of phases to simulate.
    payoffRate -- the modifier applied to CAS missions for scoring. For instance,
                  '0.5' would mean CAS is half as effective. Defaults to 1.
    """
    
    def __init__(self, blue, red, duration, payoffRate = 1):
        self.blue = blue
        self.red = red
        self.duration = duration + 1
        self.payoffRate = payoffRate
        self.turn = 0
        self.score = 0
        
    def advance(self):
        """ Advance the simulation one turn."""
        self.turn += 1
        blueScore = self.blue.close_air_support() * self.payoffRate
        redScore = self.red.close_air_support() * self.payoffRate
        self.score += blueScore - redScore
        
        blueCasualties = self.red.airfield_attack()
        redCasualties = self.blue.airfield_attack()
        
        self.blue.damage(blueCasualties)
        self.red.damage(redCasualties)
        
        self.blue.reinforce()
        self.red.reinforce()
        
        print(self)
        
    def resolve(self):
        """ Resolve the simulation to its conclusion."""
        print("CAMPAIGN: {} vs. {}\n".format(self.blue.name, self.red.name))
        for i in range(self.duration):
            self.advance()
            
    def __str__(self):
        """ Print method override."""
        phaseString = "{:<4} | {:5}".format(self.turn, self.score)
        return phaseString
        

       
# TEST ENGAGEMENT #

blue = AirForce('Blue', 120, 0.2, 0, 2)
red = AirForce('Red', 120, 0.2, 0.3, 2)

campaign = AirCampaign(blue, red, 30)
campaign.resolve()