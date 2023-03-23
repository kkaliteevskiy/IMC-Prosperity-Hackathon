# BEWARE - WITH THE ADDITION OF A FOR LOOP FOR price, THIS PROGRAM WILL TAKE A LONG TIME TO RUN

import random
import numpy as np
import matplotlib.pylab as plt

pnl_expected = {}

print("BEGINNING SIMULATION. THIS MAY TAKE SOME TIME. SEE PROGRESS BAR:")
print("."*80)
for price in range(10000, 11000, 10):

    our_price = price
    price_range = (9000, 11000)

    number_of_crates = 300
    pineapples_per_crate = 4
    pineapple_value = 2500

    average_earnings = []
    average_of_the_averages = []


    for lower_bound in range(10000, 11001, 10):
        # run 100 random simulations
        for i in range(100):
            # create 999 simulated group bids
            # worst case would be where they all bid 11000, best case is probably a random spread in the price range
            group_bids = [random.randint(lower_bound, 11000) for i in range(999)] # create 999 group bids

            group_bids.append(our_price)
            group_bids.sort()

            lowest_half = group_bids[0:500] # lowest 50% of bids
            average = np.mean(lowest_half)

            #print("\nour bid: ", our_price)
            #print("upper bound for lower half: ", lowest_half[-1])
            #print("average price: ", average)

            if (our_price in lowest_half):
                profit_margin_per_crate = our_price - average
                expected_earnings = number_of_crates * profit_margin_per_crate
                #print("we can expect to earn: ", expected_earnings)
            else:
                expected_earnings = 0.0
                #print("price not in bottom 50%, expect to earn 0")
            average_earnings.append(expected_earnings)

        #print("\nBased on an average over all the simulations, the expected value is ", np.mean(average_earnings))
        average_of_the_averages.append(np.mean(average_earnings))

    #print("\nBased on simulations with varying distributions, the expected profit/loss is: ", np.mean(average_of_the_averages))
    pnl_expected[price] = (np.mean(average_of_the_averages))
    progress = "." * round(80*(price-10000)/(11000-10000))
    print("\r"+progress,end="")

best_price = max(pnl_expected, key=pnl_expected.get)
max_val = pnl_expected.get(best_price)
print("Optimum solution is to price at ", best_price, " with an expected profit of ", max_val)

lists = sorted(pnl_expected.items())
x,y = zip(*lists)
plt.plot(x,y)
plt.show