import random



numberoftanks = 1200
serialnumbers = [i+1 for i in range(numberoftanks)]
random.shuffle(serialnumbers)

sample = 15
sampleserials = serialnumbers[:sample]

def estimate_tanks(sample):
    estimate = max(sampleserials) + (max(sampleserials) / len(sampleserials)) - 1
    return round(estimate)
    
print(estimate_tanks(sampleserials))