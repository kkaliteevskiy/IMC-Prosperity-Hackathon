# Code which will be required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.

from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np

class Trader:
        
    past_100_valuations = {"PEARLS": [10000], "BANANAS": [5000], "PINA_COLADAS": [15000], "COCONUTS": [8000]}
    rolling_average_trading_price = {"PEARLS": 10000, "BANANAS": 5000, "PINA_COLADAS": 15000, "COCONUTS": 8000}


    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # set position limits and estimate fair values
        positionLimits = {"PEARLS": 20, "BANANAS": 20, "PINA_COLADAS": 600, "COCONUTS": 300}
        productValuations = {"PEARLS": 10000, "BANANAS": 4890, "PINA_COLADAS": 15000, "COCONUTS": 8000}

        currentValuations = get_current_market_prices(state.market_trades)

        for product in currentValuations.keys():#define rolling average for each product

            if(len(Trader.past_100_valuations[product]) < 10):#if less than 100 trades took place
                Trader.past_100_valuations[product].append(currentValuations[product])
            else:
                Trader.past_100_valuations[product] = np.roll(Trader.past_100_valuations[product], -1)#rotate and reassign 
                Trader.past_100_valuations[product][-1] = currentValuations[product] 
            
            mean_price = np.mean(Trader.past_100_valuations[product])
            Trader.rolling_average_trading_price[product] = mean_price
            print(product, ' mean price : ', mean_price)




        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            # Define a fair value
            acceptable_price = Trader.rolling_average_trading_price[product]

            # get current position and position limit on the product
            currentPosition = state.position.get(product, 0) # set to 0 if nothing returned
            positionLimit = positionLimits[product]

            # If statement checks if there are any SELL orders in the market
            if len(order_depth.sell_orders) > 0:

                # Sort all the available sell orders by their price,
                # and select only the sell order with the lowest price
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = -1*order_depth.sell_orders[best_ask]

                i = 0 # counter for selecting (i+1)th lowest available price

                # Check if the lowest ask (sell order) is lower than the above defined fair value
                while (best_ask < acceptable_price and currentPosition < positionLimit):

                    # decide how much to buy
                    quantityToBuy = self.decideHowMuchToBuy(currentPosition, best_ask_volume, positionLimit)
                    # update current position
                    currentPosition += quantityToBuy
                    
                    # We expect this order to trade with the sell order
                    #print(product, "BUY", str(quantityToBuy) + "x", best_ask)
                    orders.append(Order(product, best_ask, quantityToBuy))

                    # update to next best available price if relevant
                    i += 1
                    if (i < len(order_depth.sell_orders.keys())):
                        best_ask = sorted(order_depth.sell_orders.keys())[i]
                        best_ask_volume = -1*order_depth.sell_orders[best_ask]
                    else:
                        # stop checking prices - break out of while loop
                        break


            # The below code block is similar to the one above,
            # the difference is that it finds the highest bid (buy order)
            # If the price of the order is higher than the fair value
            # This is an opportunity to sell at a premium
            if len(order_depth.buy_orders) != 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid > acceptable_price:
                    if currentPosition - best_bid_volume > -positionLimits[product]:
                        # safe to sell all available at this price
                        quantityToSell = best_bid_volume
                    else:
                        quantityToSell = positionLimits[product] + currentPosition

                    # print(product, "SELL", str(quantityToSell) + "x", best_bid)
                    orders.append(Order(product, best_bid, -quantityToSell))

            # Add all the above orders to the result dict
            if(len(orders) >=2):#check that 2 orders have been placed
                if(orders[0].price < orders[1].price): #check that you are selling at a higher ptove than you are buying
                    result[product] = orders
            # Return the dict of orders
            # These possibly contain buy or sell orders depending on the logic above
        # print for debugging purposes 
        print("Printing output: ")
        print(result)

        return result

    def decideHowMuchToBuy(self, currentPos, maxPossibleVolume, posLimit):
        """ Decide how much of a product to buy, given that there is at least some available at a fair price
        Takes as input the current position on the product in question, the position limit for that product and the
        max available to buy at the one specific price point
        Returns how much can be bought at that price"""
        if currentPos + maxPossibleVolume <= posLimit:
            # can buy all available at that price without reaching position limit
            quantityToBuy = maxPossibleVolume
        else:
            # buy just enough to reach the position limit
            # *** might not be a great strategy to do this every time...
            quantityToBuy = posLimit - currentPos
        # update current position
        return quantityToBuy

    
def get_current_market_prices(market_trades):
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
            
def get_rolling_average_valuations(self, market_trades):

        currentValuations = self.get_current_market_prices(market_trades)
        rollingValuations = {}# Dict[Symbol, price]
        
        for product in market_trades.keys():

            if(len(self.past_100_valuations[product]) < 100):
                self.past_100_valuations[product].append(currentValuations[product])

            else:
                self.past_100_valuations[product] = np.roll(self.past_100_valuations[product], -1)# shift the array
                self.past_100_valuations[product][-1] = currentValuations[product] #set final valuation to the current valuation

                rollingValuations[product] = self.past_100_valuations[product].mean()

            print('product valuations :', rollingValuations)
            
        return currentValuations
            