# Code which will be required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.

from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np

class Trader:
    
    past_100_valuations = {"PEARLS": [10000], "BANANAS": [5000], "PINA_COLADAS": [15000], \
                           "COCONUTS": [8000], "DIVING_GEAR": [99000], "BERRIES": [3800], "DOLPHIN_SIGHTINGS": [0]}
    rolling_average_trading_price = {"PEARLS": 10000, "BANANAS": 5000, "PINA_COLADAS": 15000,\
                            "COCONUTS": 8000, "DIVING_GEAR": 99000, "BERRIES": 3800, "DOLPHIN_SIGHTINGS": 0}
    my_buy_price = {"PEARLS": 10000, "BANANAS": 5000, "PINA_COLADAS": 15000,\
                            "COCONUTS": 8000, "DIVING_GEAR": 99000, "BERRIES": 3800, "DOLPHIN_SIGHTINGS": 0}

    my_sell_price = {"PEARLS": 10000, "BANANAS": 5000, "PINA_COLADAS": 15000,\
                            "COCONUTS": 8000, "DIVING_GEAR": 99000, "BERRIES": 3800, "DOLPHIN_SIGHTINGS": 0}
    
    #dictionary for storing wether a product is rising None if stationary 
    correlation_coefficient = {"PEARLS": 0, "BANANAS": 0, "PINA_COLADAS": 0, \
                           "COCONUTS": 0, "DIVING_GEAR": 0, "BERRIES": 0, "DOLPHIN_SIGHTINGS": 0}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}



        # set position limits
        positionLimits = {"PEARLS": 20, "BANANAS": 20, "COCONUTS": 600, "PINA_COLADAS": 300,\
            "DIVING_GEAR": 50, "BERRIES": 250, "DOLPHIN_SIGHTINGS": 1}

        # set safety margins for each product - a measure of how confident we can be in the valuation
        # smaller margin = more confident in valuation
        
        product_cost_margin = {"PEARLS": 1, "BANANAS": 1, "PINA_COLADAS": 1, \
                                "COCONUTS": 5, "DIVING_GEAR": 25, "BERRIES": 5, "DOLPHIN_SIGHTINGS": 3}
        
        currentValuations = getCurrentMarketPrices(state.market_trades)
        
        own_trades = state.own_trades

        #Dict[product, [trades,,,]]
        own_buy_trades = {"PEARLS": [], "BANANAS": [], "PINA_COLADAS": [], "COCONUTS": [], "DIVING_GEAR": [], "BERRIES": [], "DOLPHIN_SIGHTINGS": []}
        own_sell_trades = {"PEARLS": [], "BANANAS": [], "PINA_COLADAS": [], "COCONUTS": [], "DIVING_GEAR": [], "BERRIES": [], "DOLPHIN_SIGHTINGS": []}

        #define own buy/sell prices for each product 
        for product in own_trades.keys():

            for trade in own_trades[product]: # accumilate list of own trades for each product

                if trade.buyer == 'SUBMISSION':
                    own_buy_trades[product].append(trade.price)

                else: #trade.seller == 'SUBMISSION'
                    own_sell_trades[product].append(trade.price)

                #get own sell/buy pries

                try:
                    Trader.my_sell_price[product] = max(own_sell_trades[product])
                    Trader.my_buy_price[product] = max(own_sell_trades[product])
                except:
                    Trader.my_sell_price[product] = currentValuations[product] + product_cost_margin[product]
                    Trader.my_buy_price[product] = currentValuations[product] + product_cost_margin[product]

        # define rolling average price for each product based on all market trades
        #also define if product is rising of fallling. Corrleation coefficient is used as a measure of positive or negative slope 
        for product in currentValuations.keys():
            if(len(Trader.past_100_valuations[product]) < 100):
                # less than 100 trades took place
                Trader.past_100_valuations[product].append(currentValuations[product])
            else:
                # rotate and reassign
                Trader.past_100_valuations[product] = np.roll(Trader.past_100_valuations[product], -1)
                Trader.past_100_valuations[product][-1] = currentValuations[product]
                            
            #consider the past 10 trades for calculating the rolling average and correlation coefficient

            if(len(Trader.past_100_valuations) >= 10):
                mean_price = np.mean(Trader.past_100_valuations[product][-10:])
                correlation_coefficient = np.corrcoeff(x = np.arrange(0, 10), y = Trader.past_100_valuations[product][-10:])
            else:
                mean_price = Trader.past_100_valuations[product][0]#default value
                correlation_coefficient = 0

            if product == "PEARLS":
                mean_price = 10000 # hard code to set pearl acceptable_price to 10000 as an exception

            Trader.rolling_average_trading_price[product] = mean_price
            Trader.correlation_coefficient[product] = correlation_coefficient
        
        # Iterate over all the keys (the available products) contained in the order depths 
        for product in state.order_depths.keys():

            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            # estimate a fair value
            # can mess with this eg. by changing -safetymargins to +safetyMargins will making buying more likely
            acceptable_buy_price = Trader.rolling_average_trading_price[product] - product_cost_margin[product]
            acceptable_sell_price = Trader.rolling_average_trading_price[product] + product_cost_margin[product]

            # get current position and position limit on the product
            currentPosition = state.position.get(product, 0) # set to 0 if nothing returned
            positionLimit = positionLimits[product]

            if product == "BERRIES":
                if state.timestamp < 30000:
                    acceptable_buy_price = 100000 # encourage trader to buy as much as possible
                    acceptable_sell_price = 100000 # discourage trader from selling
                elif 47500 < state.timestamp < 52500:
                    acceptable_buy_price = 1 # discourage buying at peak
                    acceptable_sell_price = 1 # encourage selling at peak

            # If statement checks if there are any SELL orders in the market
            if len(order_depth.sell_orders) > 0:

                # Sort all the available sell orders by their price,
                # and select only the sell order with the lowest price
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = -1*order_depth.sell_orders[best_ask]

                # Check if the lowest ask (sell order) is lower than the above defined fair value
                if best_ask < acceptable_buy_price and Trader.correlation_coefficient[product] >= 0: #also check that the porduct price is rising

                    # decide how much to buy
                    if product == "PEARLS":
                        quantityToBuy = decideHowMuchCanBeBought(currentPosition, best_ask_volume, positionLimit)
                    else:
                        quantityToBuy = decideHowMuchToBuy(currentPosition, best_ask_volume, positionLimit, best_ask, acceptable_buy_price)
                    
                    if quantityToBuy != 0:                    
                        # We expect this order to trade with the sell order
                        print(product, "BUY", str(quantityToBuy) + "x", best_ask)
                        orders.append(Order(product, best_ask, quantityToBuy))


            # Tuhe below code block looks for opportunities to sell at a premim 
            if len(order_depth.buy_orders) != 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid > acceptable_sell_price and Trader.correlation_coefficient[product] <= 0:
                    if product == "PEARLS":
                        quantityToSell = decideHowMuchCanBeSold(currentPosition, best_bid_volume, positionLimit)
                    else:
                        quantityToSell = decideHowMuchToSell(currentPosition, best_bid_volume, positionLimit, best_bid, acceptable_sell_price)

                    if quantityToSell != 0:
                        print(product, "SELL", str(quantityToSell) + "x", best_bid)
                        orders.append(Order(product, best_bid, -quantityToSell))

            # Add all the above orders to the result dict
            result[product] = orders

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
    return quantityToSell

def decideHowMuchToSell(currentPos, maxPossibleVolume, posLimit, sellingPrice, estimatedValue):
    """analogous to decideHowMuchToBuy() - see that function for explanation"""
    maxAmount = decideHowMuchCanBeSold(currentPos, maxPossibleVolume, posLimit)
    weight = abs(sellingPrice - estimatedValue)
    #activation = sigmoid(5*(weight+0.3))
    activation = sigmoid(weight) # need slightly different activation as weight is different
    quantityToSell = round(maxAmount * activation)
    return quantityToSell


def getProductValuations(order_depths):
    """Looks at the order_depths and calculates the current market price of products"""

    predicted_prices = {}

    for product in order_depths.keys():

        best_ask = min(order_depths[product].sell_orders.keys())
        best_bid = max(order_depths[product].buy_orders.keys())
        mid_price = (best_ask + best_bid) / 2
        try:
            predicted_prices[product] = mid_price
        except Exception:
            predicted_prices[product] = -1 # throw a nonsense price which can be picked up easily

    return predicted_prices

def updateProductValuations(orderDepths, prevPrices):
    """Attempt to get new estimates for product valuations
    Update prevPrices: Dict[Symbol, int] iff getProductValuations() returns a logical estimate"""
    predictedPrices = getProductValuations(orderDepths)
    for prod in predictedPrices.keys():
        if predictedPrices[prod] != -1:
            # getProductValuations did not throw an error
            prevPrices[prod] = predictedPrices[prod]
    return prevPrices

def incrementAllDictValuesByX(myDict: Dict, x: int):
    newDict = {}
    for key in myDict.keys():
        newDict[key] = myDict[key] + x
    return newDict

def getCurrentMarketPrices(market_trades):
    """Looks at the market_tardes - Dict[Symbol, List[Trade]] (trades that have been made by other market participants) 
    and calculates the current market proce of products"""

    predicted_prices = {}

    for product in market_trades.keys():

        transaction_totals = 0
        quantity_traded = 0
        
        for trade in market_trades[product]:
            transaction_totals += trade.price * abs(trade.quantity)
            quantity_traded += abs(trade.quantity)

        try:
            predicted_prices[product] = transaction_totals/quantity_traded
        except:
            predicted_prices[product] = Trader.past_100_valuations[product][0]#default value

    return predicted_prices