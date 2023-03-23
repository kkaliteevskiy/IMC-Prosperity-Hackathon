our_price = 10900
price_range = (9000, 11000)

number_of_crates = 300
pineapples_per_crate = 4
pineapple_value = 2500

average_earnings = []

import random
import numpy as np

# run 10 random simulations
for i in range(100):
    # create 999 simulated group bids
    # worst case would be where they all bid 11000, best case is probably a random spread in the price range
    group_bids = [random.randint(10800, 11000) for i in range(999)] # create 999 group bids

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
        print("we can expect to earn: ", expected_earnings)
    else:
        expected_earnings = 0.0
        print("price not in bottom 50%, expect to earn 0")
    average_earnings.append(expected_earnings)

print("\nBased on an average over all the simulations, the expected value is ", np.mean(average_earnings))

