# Code which will be required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.

from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np

class Trader:
    
    past_10_valuations = { 
        "PEARLS": [10000],
        "BANANAS": [5000],
        "PINA_COLADAS": [15000],
        "COCONUTS": [7940],
        "DIVING_GEAR": [99000],
        "BERRIES": [3800],
        "DOLPHIN_SIGHTINGS": [0],
        "BAGUETTE": [12200],
        "DIP": [7100],
        "UKULELE": [21000],
        "PICNIC_BASKET": [74000]
        }
    
    sma_trading_price = {
        "PEARLS": 10000,
        "BANANAS": 5000,
        "PINA_COLADAS": 15000,
        "COCONUTS": 8000,
        "DIVING_GEAR": 99000,
        "BERRIES": 3800,
        "DOLPHIN_SIGHTINGS": 0,
        "BAGUETTE": 12000,
        "DIP": 7000,
        "UKULELE": 20400,
        "PICNIC_BASKET": 74000
        }

    ema_trading_price = {
        "PEARLS": 10000,
        "BANANAS": 5000,
        "PINA_COLADAS": 15000,
        "COCONUTS": 8000,
        "DIVING_GEAR": 99000,
        "BERRIES": 3800,
        "DOLPHIN_SIGHTINGS": 0,
        "BAGUETTE": 12000,
        "DIP": 7000,
        "UKULELE": 20400,
        "PICNIC_BASKET": 74000
    }
    k = {# k for calculating emas , if 1, then ema = current valuations
        "PEARLS": 1, #perhaps not applicable
        "BANANAS": 1,# try no algo for bananas works
        "PINA_COLADAS": 0.05,# this ema works well 
        "COCONUTS": 0.05,#works okay 
        "DIVING_GEAR": 1,
        "BERRIES": 1,
        "DOLPHIN_SIGHTINGS": 0,
        "BAGUETTE": 0.02,
        "DIP": 0.01,#not sure about this one
        "UKULELE": 1,
        "PICNIC_BASKET": 1
    }
    
    last_dolphin_sighting = 0
    diving_gear_start_time = -100000 # initialise to negatively large number
    picnic_components = ["DIP", "UKULELE", "BAGUETTE"]
    picnic_basket_differential = 0
    correlation_coefficients = {
        "PEARLS": 0,
        "BANANAS": 0,
        "PINA_COLADAS": 0,
        "COCONUTS": 0,
        "DIVING_GEAR": 0,
        "BERRIES": 0,
        "DOLPHIN_SIGHTINGS": 0,
        "BAGUETTE": 0,
        "DIP": 0,
        "UKULELE": 0,
        "PICNIC_BASKET": 0
    }
    correlations_to_set = ["BERRIES", "DIVING_GEAR", "PINA_COLADAS", "COCONUTS", "BANANAS"]

    use_ema_or_sma = {
        "PEARLS": 'none',
        "BANANAS": 'none',
        "PINA_COLADAS": 'ema',
        "COCONUTS": 'ema',
        "DIVING_GEAR": 'sma',
        "BERRIES": 'sma',
        "DOLPHIN_SIGHTINGS": 'none',
        "BAGUETTE": 'ema',
        "DIP": 'sma',
        "UKULELE": 'sma',
        "PICNIC_BASKET": 'sma'
    }

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # set position limits
        positionLimits = {"PEARLS": 20, "BANANAS": 20, "COCONUTS": 600, "PINA_COLADAS": 300,\
            "DIVING_GEAR": 50, "BERRIES": 250, "DOLPHIN_SIGHTINGS": 0,\
            "BAGUETTE": 150, "DIP": 300, "UKULELE": 70, "PICNIC_BASKET": 70}

        # set safety margins for each product - a measure of how confident we can be in the valuation
        # smaller margin = more confident in valuation
        safetyMargins = {"PEARLS": 0, "BANANAS": 0, "COCONUTS": 0, "PINA_COLADAS": 0,\
            "DIVING_GEAR": 0, "BERRIES": 0, "DOLPHIN_SIGHTINGS": 0,\
            "BAGUETTE": 0, "DIP": 0, "UKULELE": 0, "PICNIC_BASKET": 0} 
        
        currentValuations = getCurrentMarketPrices(state.market_trades)
        
        # define rolling average and exponential moving average price for each product
        for product in currentValuations.keys():
            if(len(Trader.past_10_valuations[product]) < 10):
                # less than 100 trades took place
                Trader.past_10_valuations[product].append(currentValuations[product])
            else:
                # rotate and reassign
                Trader.past_10_valuations[product] = np.roll(Trader.past_10_valuations[product], -1)
                Trader.past_10_valuations[product][-1] = currentValuations[product]            
            mean_price = np.mean(Trader.past_10_valuations[product])
            ema = (1-Trader.k[product]) * Trader.ema_trading_price[product] + Trader.k[product] * currentValuations[product]

            
            # set correlation coefficients - only for some of the products - otherwise will remain 0
            if product in Trader.correlations_to_set:
                correlation_coeff = np.corrcoef(x=np.arange(0,len(Trader.past_10_valuations[product])), y=Trader.past_10_valuations[product])[0][1]
                Trader.correlation_coefficients[product] = correlation_coeff
            # special action for certain products
            if product == "PEARLS":
                mean_price = 10000 # hard code to set pearl acceptable_price to 10000 as an exception
            elif product == "PICNIC_BASKET":
                Trader.picnic_basket_differential = calculateBasketVsCombined()
                mean_price -= Trader.picnic_basket_differential / 2
            elif product in Trader.picnic_components: # dip, baguette or ukulele
                # TODO add something here to make it product specific
                mean_price += Trader.picnic_basket_differential / 2
                
            Trader.sma_trading_price[product] = mean_price
            Trader.ema_trading_price[product] = ema
        
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            # estimate a fair value
            # can mess with this eg. by changing -safetymargins to +safetyMargins will making buying more likely

            if(Trader.use_ema_or_sma[product] == 'ema'):
                acceptable_buy_price = Trader.ema_trading_price[product] - safetyMargins[product]
                acceptable_sell_price = Trader.ema_trading_price[product] + safetyMargins[product]
            elif(Trader.use_ema_or_sma[product] == 'sma'):
                acceptable_buy_price = Trader.sma_trading_price[product] - safetyMargins[product]
                acceptable_sell_price = Trader.sma_trading_price[product] + safetyMargins[product]
            else:
                acceptable_buy_price = Trader.sma_trading_price[product] - safetyMargins[product]
                acceptable_sell_price = Trader.sma_trading_price[product] + safetyMargins[product]

            # get current position and position limit on the product
            currentPosition = state.position.get(product, 0) # set to 0 if nothing returned
            positionLimit = positionLimits[product]

            if product == "BERRIES":
                if 200000 < state.timestamp < 300000:
                    acceptable_buy_price = 100000 # encourage trader to buy as much as possible
                    acceptable_sell_price = 100000 # discourage trader from selling
                elif 475000 < state.timestamp < 525000:
                    acceptable_buy_price = 1 # discourage buying at peak
                    acceptable_sell_price = 1 # encourage selling at peak
                elif 800000 < state.timestamp < 900000:
                    acceptable_buy_price += 500 # encourage buying somewhat
                    acceptable_sell_price += 500 # discourage selling somewhat
            elif product == "DIVING_GEAR":
                # check for a jump in dolphin sightings, encourage purchase of diving gear if relevant
                current_dolphin_sightings = state.observations['DOLPHIN_SIGHTINGS']
                if state.timestamp < 100:
                    # not enough data yet
                    Trader.last_dolphin_sighting = current_dolphin_sightings
                elif current_dolphin_sightings - Trader.last_dolphin_sighting > 2:
                    # jump in dolphin sightings, project price of diving gear to rise soon
                    diving_gear_price = acceptable_buy_price + 1000
                    Trader.diving_gear_start_time = state.timestamp
                
                # check if we are still in the projected rise zone for diving gear which follows a jump in dolphin sightings
                if state.timestamp - Trader.diving_gear_start_time <= 70000:
                    # assume price will rise up to the fixed value diving_gear_price
                    acceptable_buy_price = diving_gear_price
                    acceptable_sell_price = 3*diving_gear_price # basically stop sales completely


            # If statement checks if there are any SELL orders in the market
            if len(order_depth.sell_orders) > 0:
                # Sort all the available sell orders by their price,
                # and select only the sell order with the lowest price
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = -1*order_depth.sell_orders[best_ask]
                # Check if the lowest ask (sell order) is lower than the above defined fair value
                # and that product price is rising
                if best_ask < acceptable_buy_price and Trader.correlation_coefficients[product] >= 0:

                    # decide how much to buy
                    if product == "PEARLS":
                        quantityToBuy = decideHowMuchCanBeBought(currentPosition, best_ask_volume, positionLimit)
                    else:
                        quantityToBuy = decideHowMuchToBuy(currentPosition, best_ask_volume, positionLimit, best_ask, acceptable_buy_price)
                    
                    if quantityToBuy != 0:                    
                        # We expect this order to trade with the sell order
                        print(product, "BUY", str(quantityToBuy) + "x", best_ask)
                        orders.append(Order(product, best_ask, quantityToBuy))

            # The below code block looks for opportunities to sell at a premium
            if len(order_depth.buy_orders) != 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid > acceptable_sell_price and Trader.correlation_coefficients[product] <= 0:
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
    # this will range from 0 (buyingPrice == estimatedValue) to estimatedValue (buyingPrice==0)
    weight = abs(estimatedValue - buyingPrice)
    
    # now we want to bias towards results with a weight close to 1,
    # ie. where the price is very good compare to the estimated value
    # here we use a sigmoid function as an activation function to do this
    # the output of the function is also a weight ranging from 0 to 1
    activation = sigmoid(0.4*weight)
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
    activation = sigmoid(0.4*weight)
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
            predicted_prices[product] = Trader.past_10_valuations[product][0]#default value

    return predicted_prices

def calculateBasketVsCombined():
    '''calculates the difference between basket price vs the combined price of the goods'''
    basketPrice = np.mean(Trader.past_10_valuations["PICNIC_BASKET"])
    dipPrice = np.mean(Trader.past_10_valuations["DIP"])
    ukulelePrice = np.mean(Trader.past_10_valuations["UKULELE"])
    baguettePrice = np.mean(Trader.past_10_valuations["BAGUETTE"])
    combinedPrice = 2 * baguettePrice + 4 * dipPrice + ukulelePrice
    return (basketPrice - combinedPrice)