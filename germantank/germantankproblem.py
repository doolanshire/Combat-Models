""" A playful implementation of the famous "German Tank Problem" in statistics.

    First, the random number generator populates a list of "tanks", represented
    by sequential serial numbers. The numbers are added to the list in random
    order until they run out.
    
    We then choose the sample size, representing the number of tanks we have
    captured in battle and whose serial number we have been able to observe.
    
    The program then retrieves an amount of random serial numbers equal to our
    specified sample size, and attempts to estimate how many tanks there are
    in total.
    
    The formula can make fairly accurate estimates with relatively small sample
    sizes, providing the serial numbers sampled are reasonably random.
"""

from random import sample

    
def generate_serials(total, samplesize):
    """ Generate a list of consecutive serial numbers up to the specified limit
    ("total") and return a random sample out of it, of size "sample".
    """
    
    serialnumbers = [i+1 for i in range(total)]
    randomised =  sample(serialnumbers, samplesize)
    return randomised
    
def estimate_tanks(sample):
    estimate = max(sample) + (max(sample) / len(sample)) - 1
    return round(estimate)

def experiment(realtanks, samplesize):
    """ Create a virtual tank army of size "realktanks", and retrieve a random
    sample of serial numbers sized "samplesize". Then attempt to estimate the
    number "realtanks" from that sample.
    """    
    
    capturedtanks = generate_serials(realtanks, samplesize)
    
    estimate = estimate_tanks(capturedtanks)
    
    print("GERMAN TANK PROBLEM\n")
    print("Actual number of tanks: {}".format(realtanks))
    print("Sample size: {}".format(samplesize))
    print("Serial numbers sampled:")
    print(capturedtanks)
    print("-----")
    print("Estimated number of tanks: {}".format(estimate))
    
    error = abs(realtanks - estimate) / realtanks
    
    percentageoff = round(error * 100, 2)
    
    print("Error: {}%".format(percentageoff))

experiment(1500, 20)