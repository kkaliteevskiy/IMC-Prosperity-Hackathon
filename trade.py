# Code which will be required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.

from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np

# initialise market values (estimate)
lastMarketValues = {"PEARLS": 10000, "BANANAS": 4910, "COCONUTS": 8000, "PINA_COLADAS": 15000}

class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict and declare existence of global variable
        result = {}
        global lastMarketValues

        # set position limits
        positionLimits = {"PEARLS": 20, "BANANAS": 20, "COCONUTS": 600, "PINA_COLADAS": 300}

        # set safety margins for each product - a measure of how confident we can be in the valuation
        # smaller margin = more confident in valuation
        safetyMargins = {"PEARLS": 0, "BANANAS": 5, "COCONUTS": 10, "PINA_COLADAS": 10} 

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            # estimate a fair value
            acceptable_buy_price = lastMarketValues[product] - safetyMargins[product]
            acceptable_sell_price = lastMarketValues[product] + safetyMargins[product]

            # get current position and position limit on the product
            currentPosition = state.position.get(product, 0) # set to 0 if nothing returned
            positionLimit = positionLimits[product]

            # If statement checks if there are any SELL orders in the market
            if len(order_depth.sell_orders) > 0:

                # Sort all the available sell orders by their price,
                # and select only the sell order with the lowest price
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]

                # Check if the lowest ask (sell order) is lower than the above defined fair value
                if best_ask < acceptable_buy_price:

                    # decide how much to buy
                    quantityToBuy = decideHowMuchToBuy(currentPosition, best_ask_volume, positionLimit, best_ask, acceptable_buy_price)
                    # update current position
                    currentPosition += quantityToBuy
                    
                    # We expect this order to trade with the sell order
                    print(product, "BUY", str(quantityToBuy) + "x", best_ask)
                    orders.append(Order(product, best_ask, quantityToBuy))


            # The below code block looks for opportunities to sell at a premium
            if len(order_depth.buy_orders) != 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid > acceptable_sell_price:
                    quantityToSell = decideHowMuchToSell(currentPosition, best_bid_volume, positionLimit, best_bid, acceptable_sell_price)

                    # update current position
                    currentPosition -= quantityToSell

                    print(product, "SELL", str(quantityToSell) + "x", best_bid)
                    orders.append(Order(product, best_bid, -quantityToSell))

            # Add all the above orders to the result dict
            result[product] = orders

        # update market values
        lastMarketValues = updateProductValuations(state.market_trades, lastMarketValues)

        # Return the dict of orders
        # These possibly contain buy or sell orders depending on the logic above
        return result

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def decideHowMuchCanBeBought(currentPos, maxPossibleVolume, posLimit):
    """ Decide how much of a product can be bought, given that there is at least some available at a fair price
    Takes as input the current position on the product in question, the position limit for that product and the
    max available to buy at the one specific price point
    Returns how much can be bought at that price"""
    if currentPos + maxPossibleVolume <= posLimit:
        # can buy all available at that price without reaching position limit
        quantityToBuy = maxPossibleVolume
    else:
        # buy just enough to reach the position limit
        quantityToBuy = posLimit - currentPos
    print("buy pos", currentPos, "max", quantityToBuy, "limit", posLimit, "maxPoss", maxPossibleVolume)
    return quantityToBuy

def decideHowMuchToBuy(currentPos, maxPossibleVolume, posLimit, buyingPrice, estimatedValue):
    maxAmount = decideHowMuchCanBeBought(currentPos, maxPossibleVolume, posLimit)
    # calculate a weighted score, based on how close the purchase price is to the estimated value
    # this will range from 0 (buyingPrice == estimatedValue) to 1 (buyingPrice==0)
    weight = abs(estimatedValue - buyingPrice)/estimatedValue
    
    # now we want to bias towards results with a weight close to 1,
    # ie. where the price is very good compare to the estimated value
    # here we use a sigmoid function as an activation function to do this
    # the output of the function is also a weight ranging from 0 to 1
    activation = sigmoid(5*weight) + 0.00669285
    quantityToBuy = round(maxAmount * weight * activation)
    return quantityToBuy

def decideHowMuchCanBeSold(currentPos, maxPossibleVolume, posLimit):
    """analogous to decideHowMuchCanBeBought() - see that function for explanation"""
    if currentPos - maxPossibleVolume > -posLimit:
        # safe to sell all available at this price
        quantityToSell = maxPossibleVolume
    else:
        quantityToSell = posLimit + currentPos
    print("pos", currentPos, "max", quantityToSell)
    return quantityToSell

def decideHowMuchToSell(currentPos, maxPossibleVolume, posLimit, sellingPrice, estimatedValue):
    """analogous to decideHowMuchToBuy() - see that function for explanation"""
    maxAmount = decideHowMuchCanBeSold(currentPos, maxPossibleVolume, posLimit)
    weight = abs(sellingPrice - estimatedValue)
    #activation = sigmoid(5*(weight+0.3))
    activation = sigmoid(weight) # need slightly different activation as weight is different
    quantityToSell = round(maxAmount * activation)
    print(".......",weight, activation, maxAmount*activation)
    return quantityToSell


def getProductValuations(market_trades):
    """Looks at the market_trades: Dict[Symbol, List[Trade]] (trades that have been made by other market participants) 
    and calculates the current market price of products"""

    predicted_prices = {}

    for product in market_trades.keys():

        transaction_totals = 0
        quantity_traded = 0
        
        for trade in market_trades[product]:
            transaction_totals += trade.price * abs(trade.quantity)
            quantity_traded += abs(trade.quantity)

        try:
            predicted_prices[product] = transaction_totals/quantity_traded
        except ZeroDivisionError:
            predicted_prices[product] = -1 # throw a nonsense price which can be picked up easily

    return predicted_prices

def updateProductValuations(marketTrades, prevPrices):
    """Attempt to get new estimates for product valuations
    Update prevPrices: Dict[Symbol, int] iff getProductValuations() returns a logical estimate"""
    predictedPrices = getProductValuations(marketTrades)
    for prod in predictedPrices.keys():
        if predictedPrices[prod] != -1:
            # getProductValuations did not throw a ZeroDivisionError
            prevPrices[prod] = predictedPrices[prod]
    return prevPrices

def incrementAllDictValuesByX(myDict: Dict, x: int):
    newDict = {}
    for key in myDict.keys():
        newDict[key] = myDict[key] + x
    return newDict