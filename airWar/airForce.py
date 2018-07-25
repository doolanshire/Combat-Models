class AirForce:
    '''One of two competing air forces in a campaign.'''
    
    def __init__(self, name, planes, killRate, CASratio = 0, reinforcements = 0):
        self.name = name
        self.planes = planes
        self.killRate = killRate
        self.CASratio = CASratio
        self.reinforcements = reinforcements
        
    def airfield_attack(self):
        return round(int(self.planes * (1 - self.CASratio)) * self.killRate)
        
    def close_air_support(self):
        return int(self.planes * self.CASratio)
        
    def damage(self, amount):
        self.planes -= amount
        if self.planes < 0:
            self.planes = 0
            
    def reinforce(self):
        self.planes += self.reinforcements
        
class AirCampaign:
    ''' A campaign between two air forces, with a given duration.'''
    
    def __init__(self, blue, red, duration, payoffRate = 1):
        self.blue = blue
        self.red = red
        self.duration = duration + 1
        self.payoffRate = payoffRate
        self.turn = 0
        self.score = 0
        
    def advance(self):
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
        
        print(self.score)
        
    def resolve(self):
        for i in range(self.duration):
            self.advance()
        

       
# UNIT TESTS #

blue = AirForce('Blue', 120, 0.2, 0, 2)
red = AirForce('Red', 120, 0.2, 0.3, 2)

campaign = AirCampaign(blue, red, 30)
campaign.resolve()