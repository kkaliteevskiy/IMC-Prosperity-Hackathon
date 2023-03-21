# script to try find the optimum manual trades for day 1

exchangeRates = {
#            pizzaSlice wasabiRoot snowball shells
'pizzaSlice': [1,        0.5,        1.45,   0.75], # from pizzaSlice
'wasabiRoot': [1.95,     1,          3.1,    1.49], # from wasabiRoot
'snowball':   [0.67,     0.31,       1,      0.48], # from snowball
'shells':     [1.34,     0.64,       1.98,   1   ], # from shells
}

# set corresponding index for each item
indexDict = {
    0: 'pizzaSlice',
    1: 'wasabiRoot',
    2: 'snowball',
    3: 'shells'
}

# intialise array of possible total exchange rates
totalRates = [1]
bestTradeItemInfo = []
bestTradeRateInfo = []

# loop through all possibilities and calculate total exchange rate
for rate1 in exchangeRates['shells']: # have to start from shells
    index = exchangeRates['shells'].index(rate1)
    currentItem1 = indexDict[index]
    
    for rate2 in exchangeRates[currentItem1]:
        index2 = exchangeRates[currentItem1].index(rate2)
        currentItem2 = indexDict[index2]

        for rate3 in exchangeRates[currentItem2]:
            index3 = exchangeRates[currentItem2].index(rate3)
            currentItem3 = indexDict[index3]

            for rate4 in exchangeRates[currentItem3]:
                index4 = exchangeRates[currentItem3].index(rate4)
                currentItem4 = indexDict[index4]

                rate5 = exchangeRates[currentItem4][3] # have to end on shells
                totalRate = rate1 * rate2 * rate3 * rate4 * rate5

                if (totalRate > max(totalRates)):
                    # new best rate - store trade information
                    bestTradeItemInfo = ['shells', currentItem1, currentItem2, currentItem3, currentItem4, 'shells']
                    bestTradeRateInfo = [rate1, rate2, rate3, rate4, rate5]
                    
                    print('\nNew best trade rate: ', totalRate)
                    print(bestTradeItemInfo)
                    print(bestTradeRateInfo)

                elif (totalRate == max(totalRates)):
                    # joint best rate - print trade information
                    print("\nJoint best rate - trade info:")
                    print('shells', currentItem1, currentItem2, currentItem3, currentItem4, 'shells')
                    print(rate1, rate2, rate3, rate4, rate5)
                    print(totalRate)
                
                totalRates.append(totalRate)


bestRate = max(totalRates)

print("\nTotal trades explored: ", len(totalRates)-1) # -1 because list was not empty when initialised
print("Best trade rate found: ", bestRate)
print("Info for best trade found: ")
print(bestTradeRateInfo)
print(bestTradeItemInfo)


i = 0
for rate in totalRates:
    if rate == bestRate:
        i += 1
print("\nNumber of trade options with best possible rate: ", i)