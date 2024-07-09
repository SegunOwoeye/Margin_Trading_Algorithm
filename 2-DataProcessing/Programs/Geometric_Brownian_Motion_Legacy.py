import math
import numpy as np
import numpy.random as npr 
#from pylab import plt, mpl
import matplotlib.pyplot as plt
import scipy.stats as scs


I = 100000 #Number of Monte Carlo Simulaions
T = 1/365/24 # Time in Years (translated to hours)
#dt = T / M # Time Step
sigma = 0.25 # The constant volatility factor
r = 0.05 # The constant riskless short rate -> Stable coin interest rate


#S = np.zeros((M + 1, I))
S0 = 69000 # Initial Index Level
mu = (r - 0.5 * sigma ** 2) # Expected Return (Drift Term)


npr.seed(21)
ST2 = S0 * npr.lognormal(mu * T, sigma * math.sqrt(T), size=I)

#print(S[-1])

plt.figure(figsize=(10, 6))
plt.hist(ST2, bins=50)
plt.xlabel('Price')
plt.ylabel('frequency')

"""plt.figure(figsize=(10, 6))
plt.plot(ST2[:50], lw=1.5)
plt.xlabel('time')
plt.ylabel('index level')"""

plt.show()



def print_statistics(a2):
    ''' Prints selected statistics.
    Parameters
    ==========
    a1, a2: ndarray objects
    results objects from simulation
    '''
    sta2 = scs.describe(a2)

    #print(sta1)
    print('%14s %14s' % ('statistic', 'data set 2'))
    print(35 * "-")
    print('%14s %14.3f' % ('size', sta2[0]))
    print('%14s %14.3f' % ('min', sta2[1][0]))
    print('%14s %14.3f' % ('max', sta2[1][1]))
    print('%14s %14.3f' % ('mean', sta2[2]))
    print('%14s %14.3f' % ('std', np.sqrt(sta2[3])))
    print('%14s %14.3f' % ('skew', sta2[4]))
    print('%14s %14.3f' % ('kurtosis', sta2[5]))

print_statistics(ST2)