# German Tank Problem
A playful implementation of the famous "German Tank Problem" in statistics.
## Description
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